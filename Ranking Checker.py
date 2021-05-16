import requests
import urllib.parse as p
import pandas as pd
from codetiming import Timer
import datetime
import time

import tkinter as tk
from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import tkinter.scrolledtext as ScrolledText

import logging
import traceback


logging.basicConfig(filename='tmp/myapp.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

root = Tk()
root.title('Ranking Checker')
root.geometry('650x490')


def Info():
    tkinter.messagebox.showinfo(
        'Info', 'This program shows the google ranking of your target webpage for the keywords entered. '
        '\n\nBefore hitting Run please ensure that you have entered'
        ' both a target and at least one keyword.'
        '\n\nTarget needs to be a valid hostname e.g. python.org.'
        '\n\nThe keywords need to be entered as a comma separated list.'
        '\n\nYou can choose the number of google pages you would like to check from the dropdown.')


def myClick():

    t = Timer(name="class")
    t.start()

    current_time = datetime.datetime.fromtimestamp(
        time.time()).strftime("%Y-%m-%d %H:%M:%S")
    st.insert(tk.INSERT, f'\n {current_time} - Run started')
    st.yview(tk.END)
    root.update()

    try:

        search_engine = []

        with open('searchengine.txt', 'rt') as f:
            for line in f:
                search_engine.append(line.strip())

        # get the API KEY here: https://developers.google.com/custom-search/v1/overview
        API_KEY = search_engine[0]
                
        # get the search engine setup here: https://programmablesearchengine.google.com/cse/all
        SEARCH_ENGINE_ID = search_engine[1]

        results = {}

        pages = clicked.get()
        target_domain = target_textbox.get("1.0","end-1c")
        keywords_data = keyword_textbox.get("1.0","end-1c")
        
        if target_domain and keywords_data:
            
            keywords_data = keywords_data.split(',')

            for index, query in enumerate(keywords_data):

                current_time = datetime.datetime.fromtimestamp(
                            time.time()).strftime("%H:%M:%S")

                st.insert(tk.INSERT, f'\n {current_time} - Checking {query} ...')
                st.yview(tk.END)
                root.update()

                for page in range(1, pages+1):
                    st.insert(tk.INSERT, f'\n Going for page {page} ...')
                    st.yview(tk.END)
                    root.update()
                    
                    # calculating start 
                    start = (page - 1) * 10 + 1

                    # make API request
                    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}"
                    
                    data = requests.get(url).json()
                    search_items = data.get("items")
                    found = False
                    if search_items:

                        for i, search_item in enumerate(search_items, start=1):

                            title = search_item.get("title")
                            snippet = search_item.get("snippet")
                            html_snippet = search_item.get("htmlSnippet")
                            link = search_item.get("link")
                            domain_name = p.urlparse(link).netloc

                            if domain_name.endswith(target_domain):
                               
                                # get the page rank
                                rank = i + start - 1

                                st.insert(tk.INSERT, f'\n Found {target_domain} on rank #{rank} for keyword: {query}')
                                st.yview(tk.END)
                                root.update()
                            
                                # target domain is found, exit out of the program
                                found = True
                                results.update({index:{'Keyword':query,'Rank':rank,'Title':title,'Snippet':snippet,'Url':link}})
                                break
                        if found:
                            break
                    else:
                        st.insert(tk.INSERT, f'\n Page {page} not available')
                        st.yview(tk.END)
                        root.update()
                        break
                if not found:
                    results.update({index:{'Keyword':query,'Rank':'Not Available','Title':'Not Available','Snippet':'Not Available','Url':'Not Available'}})
                    st.insert(tk.INSERT, f'\n {target_domain} could not be found on first {pages} pages')
                    st.yview(tk.END)
                    root.update()

                myProgress['value'] += 100 / len(keywords_data)
                root.update()

            final_results = pd.DataFrame.from_dict(results, orient='index')
            final_results.to_csv('results.csv')

            time_spent = t.stop()
            st.insert(tk.INSERT, f'\n Total time spent - {time_spent} seconds')
            st.yview(tk.END)
            root.update()
        else:
            if not target_domain:
                tkinter.messagebox.showerror(
                    'Error',
                    'Please enter target!')
            
            if not keywords_data:
                tkinter.messagebox.showerror(
                    'Error',
                    'Please enter at least one keyword!')
            
    except Exception as e:
        logger.error(traceback.format_exc())
        tkinter.messagebox.showerror(
                'Error',
                'Something went wrong, please try again later')

target_label = Label(root, text="Target:")
target_label.place(x=50,y=12)
pages_label = Label(root, text="Pages:")
pages_label.place(x=450,y=12)
keywords_label = Label(root, text="Keywords:")
keywords_label.place(x=32,y=50)

# Dropdown menu options
options = [1,2,3,4,5,6,7,8,9,10]
  
# datatype of menu text
clicked = IntVar()
  
# initial menu text
clicked.set(3)
  
# Create Dropdown menu
pages_dropdown = OptionMenu( root , clicked , *options )
pages_dropdown.place(x=495, y=10, width=55, height=30)

target_textbox=Text(root, height=5, width=40)
target_textbox.place(x=100, y=10, width=200, height=30)

keyword_textbox=Text(root, height=5, width=40)
keyword_textbox.place(x=100, y=50, width=450, height=150)

myProgress = ttk.Progressbar(
    root,
    orient=HORIZONTAL,
    length=650,
    mode='determinate')
myProgress.place(x=0, y=250)

run_button = Button(root, text='Run', command=myClick, height=1, width=10)
run_button.place(x=180, y=210, width=75, height=30)

exit_button = Button(root, text="Exit", command=root.destroy)
exit_button.place(x=280, y=210, width=75, height=30)

info_button = Button(root, text="Info", command=Info)
info_button.place(x=380, y=210, width=75, height=30)

st = ScrolledText.ScrolledText(root)
st.configure(font='TkFixedFont')
st.grid(column=0, row=1, sticky='w', columnspan=4)
st.place(x=10, y=280, width=635, height=200)

root.mainloop()