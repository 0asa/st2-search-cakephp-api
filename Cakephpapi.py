# Written by Jad Bitar (@jadb / www.jadbitar.com)

# available commands
#   cakephpapi_search_selection
#   cakephpapi_search_from_input

# changelog
# Jad Bitar - first implementation of search selection and search from input

import sublime
import sublime_plugin

import subprocess
import webbrowser
import re
import urllib2
import os
import time

write_to = 'apigen.txt'
url = 'http://api.cakephp.org/2.4/elementlist.js'

def ParseApiList(l):
	l = l[1:(len(l)-2)]
	l = l.split('],[')
	l[0] = l[0].replace('[','')
	l[len(l)-1] = l[len(l)-1].replace(']','')
	return l

def DownloadApiList(url, write_to):
	response = urllib2.urlopen('http://api.cakephp.org/2.4/elementlist.js')
	js = response.readlines()
	for l in js:
		if l.startswith('ApiGen.elements ='):
			l = l.replace('ApiGen.elements =','').replace('"','').strip()
			l = ParseApiList(l)
			f = open(write_to,'w')
			for e in l:
				f.write('%s\n' % e)
			f.close()
			break

def isOld(filename, day = 15):
    tf = os.path.getmtime(filename)
    tn = time.time()    
    if (tn - tf) > (day*24*3600):
    	return True
    return False    

def LoadApi(url, write_to):
	if os.path.exists(write_to):
		if isOld(write_to):
			print 'Need to reload'
			DownloadApiList(url, write_to)
	else:
		DownloadApiList(url, write_to)
	f = open(write_to)
	apigen_elements = []
	for l in f:
		l = l.strip()
		apigen_elements.append(l.split(','))
	return apigen_elements

apigen_elements = LoadApi(url,write_to)

autocomplete_files = {
        'c': 'class-%s.html',
        'co': 'constant-%s.html',
        'f': 'function-%s.html',
        'm': 'class-%s.html',
        'mm': 'class-%s.html',
        'p': 'class-%s.html',
        'mp': 'class-%s.html',
        'cc': 'class-%s.html'
    }


def SearchFor(text):
    url = 'http://api20.cakephp.org/search/' + text.replace(' ','%20')
    webbrowser.open_new_tab(url)

def GoogleSearch(text):
    url = 'https://www.google.be/#q=cakephp+2.3+' + text.replace(' ','%20')
    webbrowser.open_new_tab(url)        

class HybridSearchSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for selection in self.view.sel():
            # if the user didn't select anything, search the currently highlighted word
            if selection.empty():
                text = self.view.word(selection)

            text = self.view.substr(selection)

            #response = urllib2.urlopen('http://api.cakephp.org/2.4/elementlist.js')
            #html = response.read()            

            data = [s for s in apigen_elements if text == s[1]]
            if len(data) == 1:
                data = data[0]
                
                parts = re.split('::|$',data[1])                                
                
                file = autocomplete_files[data[0]] % re.sub('[^\w]' ,'.' , parts[0].replace('(','').replace(')',''))

                if len(parts) > 1:
                    if parts[1].startswith('$'):
                        file += '#' + parts[1].replace('(','').replace(')','')
                    else:
                        file += '#_' + parts[1].replace('(','').replace(')','')

                url = 'http://api.cakephp.org/2.4/' + file
                webbrowser.open_new_tab(url)
            else:
                GoogleSearch(text)

class CakephpapiSearchSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for selection in self.view.sel():
            # if the user didn't select anything, search the currently highlighted word
            if selection.empty():
                text = self.view.word(selection)

            text = self.view.substr(selection)

            SearchFor(text)

class CakephpapiSearchFromInputCommand(sublime_plugin.WindowCommand):
    def run(self):
        # Get the search item
        self.window.show_input_panel('Search CakePHP API for', '',
            self.on_done, self.on_change, self.on_cancel)
    def on_done(self, input):
        SearchFor(input)

    def on_change(self, input):
        pass

    def on_cancel(self):
        pass
