from time import sleep
import os

import pandas as pd
import re

TEST_DOWNLOAD = False
REAL_DOWNLOAD = False
BACKUP = True

boards = ["pol", "b", "co", "g", "tv", "k", "o", "an", "sp", "asp", "sci", "his", "int", "out", "toy", "po", "ck", "lit", "mu"]
wanted_attributes = ["no", "resto", "now", "country", "country_name", "com", "replies", "board"]

#the main function of this program - gets all the posts of a given board by 
#downloading individual threads and stitching them together in a predictable manner

#the optional arguments are mostly for debugging and are not intended to be changed,
#at least not for the current application.

#we take advantage of 4chan's json api, which allows us to avoid unnecessary hurdles in 
#vulgar regexing and such. By using pandas to import the json we avoid more unpleasantries still.
def process_board(board_tag, save=True, reports=True, keep_individual_threads=False, 
                  sleep_between_requests=1, include_no_replies=False, 
                  process_individual_threads=True, max_threads=0):
    #we get the list of all active threads
    threads = pd.read_json("https://a.4cdn.org/" + board_tag + "/threads.json")

    #save it to a file
    if save:
        if not os.path.exists("data/boards/" + board_tag):
            os.makedirs("data/boards/" + board_tag)
        if keep_individual_threads and not os.path.exists("data/boards/" + board_tag + "/threads"):
            os.makedirs("data/boards/" + board_tag + "/threads")
        with open("data/boards/" + board_tag + "/" + board_tag + "_threads.csv", "w") as f:
            f.write(threads.to_csv())
    
    #make a list of individual threads to request
    thread_list = []
    for page in threads["threads"]:
        for thread in page:
            if include_no_replies or thread["replies"] > 0:
                thread_list.append(thread["no"])
    
    #Some niceties
    job_length = len(thread_list) if max_threads == 0 else max_threads
    print("Currently processing " + str(job_length) + " threads of the board /" + board_tag + "/.")
    print("ETA: " + str(job_length * sleep_between_requests) + "s.")
    
    thread_dataframe_list = []
    #if we are to proceed with downloading and potentially saving individual threads, we do it
    if process_individual_threads:
        for num, thread_id in enumerate(thread_list):
            if reports:
                print(str(1 + num) + "/" + str(job_length))
            if max_threads != 0 and num >= max_threads - 1:
                break
            sleep(sleep_between_requests)
            try:
                thread = pd.read_json("https://a.4cdn.org/" + board_tag + "/thread/" + str(thread_id) + ".json")
                thread = pd.DataFrame(list(thread["posts"]))
                thread["parent"] = thread_id
                if save and keep_individual_threads:
                    with open("data/boards/" + board_tag + "/threads/" + str(thread_id) + ".csv", "w") as f:
                        f.write(thread.to_csv())
                #keeping each thread as a dataframe
                thread_dataframe_list.append(thread)
            except Exception:
                print("thread not found")
                pass #
    
    #otherwise, we just return a list of the thread ids.
    else:
        return thread_list
    
    #we then create a dataframe of all the threads, the entries being individual posts;
    #since we add the parent's id for each given post, we can reconstruct threads at will.
    total_frame = pd.concat(thread_dataframe_list, ignore_index=True)
    total_frame["board"] = board_tag
    if save:
        with open("data/boards/" + board_tag + "/" + board_tag +  "_combined.csv", "w") as f:
            f.write(total_frame.to_csv())
    
    #we also return the frame itself for convenience - especially useful if we don't wish to commit the files to disk.
    return total_frame

#    

#we are interested in textual analysis, so we strip unnecessary symbols and numbers
def dequote_and_desymbolize(post_contents):
    try:
        html_remover = r"<.+>"
        desymbolizer = r"[^a-zA-Z' ]"
        combine_whitespace = r"\s+"

        desymbolized = re.sub(html_remover, " ", post_contents)
        desymbolized = re.sub(desymbolizer, " ", post_contents)
        desymbolized = re.sub(combine_whitespace, " ", desymbolized).strip()
        
        return desymbolized
    except:
        return None


#a small test download for debugging and such
if TEST_DOWNLOAD:
    board = process_board("pol", max_threads=5)
    board["com"] = board["com"].apply(dequote_and_desymbolize)
    board = board[wanted_attributes]


#we download all threads in all of the wanted boards, then stich them together into a single dataframe,
#not unlike what we do with posts and threads - we store the original board id likewise the thread id
if REAL_DOWNLOAD:
    posts = []
    for board in boards:
        posts.append(process_board(board))
    total_frame = pd.concat(posts, ignore_index=True)

    #processing entails prettifying the text and keeping only wished attributes
    total_frame["com"] = total_frame["com"].apply(dequote_and_desymbolize)
    total_frame = total_frame[wanted_attributes]
    
    #this we do want to write to disk, as it will be used by our analysis program
    csv = total_frame.to_csv()
    with open("data/datasets/total_dataset.csv", "w") as f:
        f.write(csv)


#backup functions, allowing one to recover from an unsuccessful stitching attempt from the collected and saved posts.
def frame_from_files():
    frames = []
    for board in boards:
        with open("data/boards/" + board + "/" + board + "_combined.csv") as f:
            frames.append(pd.read_csv(f))
    return pd.concat(frames, ignore_index=True)

if BACKUP:
    frame = frame_from_files()
    frame["com"] = frame["com"].apply(dequote_and_desymbolize)
    frame = frame[wanted_attributes]
    with open("data/datasets/total_dataset.csv", "w") as f:
        f.write(frame.to_csv())