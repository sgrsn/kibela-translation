# coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pyautogui
import pyperclip as clipboard
import re

class KibelaDriver():
    def __init__(self, url, username, password, driver_path):
        self.url = url
        self.driver = webdriver.Chrome(executable_path=driver_path)
        self.driver.get(url)
        self.login(username, password)
    
    def login(self, username, password):
        self.driver.find_element_by_xpath('//*[@id="user_email"]').send_keys(username)
        self.driver.find_element_by_xpath('//*[@id="user_password"]').send_keys(password)
        self.driver.find_element_by_xpath('//*[@id="new_user"]/div[3]/input').click()

    def get_translated(self, translation):
        ja_text_list = []
        ja_title = translation[ self.title ]
        self.add_image_sentence_in_directory(translation)       # 翻訳語のテキストに画像テキストを追加
        self.add_references_sentence_in_directory(translation)  # 翻訳語のテキストにreferencesを追加

        for en_text in self.corpus:

            if en_text in translation:
                ja_text_list.append( translation[en_text] ) 

            else:
                print('keyがないですね')
                print('key: ', en_text)
                
        ja_texts = '\n'.join(ja_text_list)

        return ja_title, ja_texts

    def write_article(self, title, text, pub=True):
        self.driver.get(self.url)
        self.driver.find_element_by_xpath('//*[@id="header"]/nav/div[2]/div[4]/div/div/div/a[1]').click()

        self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[1]/input').send_keys(title)
        time.sleep(1.0)

        codeMirror = self.driver.find_element_by_class_name("CodeMirror")
        codeMirror.find_element_by_class_name("CodeMirror-line").click()
        txtbox = codeMirror.find_element_by_css_selector("textarea")
        #txtbox.send_keys(text)
        clipboard.copy(text)
        txtbox.send_keys(Keys.CONTROL, "v")
        time.sleep(1.0)

        if pub:
            self.driver.find_element_by_class_name("editorPublishButton").click()
            time.sleep(0.5)
            self.driver.find_element_by_xpath('/html/body/div[2]/div/div/div[1]/div/div/div[4]/button[2]').click()
            time.sleep(1.0)

    def go_to_article(self, url):
        self.driver.get(url)

    def press_ctrl_A_and_ctrl_C(self):
        pyautogui.keyDown('ctrl')
        pyautogui.press('a')
        time.sleep(1.0)
        pyautogui.press('c')
        pyautogui.keyUp('ctrl')
        time.sleep(1.0)

    def copy_article(self, url):
        self.go_to_article(url+'/edit')
        time.sleep(1.0)
        txt = self.driver.find_element_by_class_name('CodeMirror-scroll')
        txt.click()
        self.press_ctrl_A_and_ctrl_C()

        title = self.driver.find_element_by_class_name('editor-titleBox-preview').text
        #text = self.driver.find_element_by_class_name('CodeMirror-scroll').text
        text = clipboard.paste()
        #text = text.replace('\u2013', '-').replace('\u2014', '-').replace('\xbc', '').replace('\ufb02', 'fl').replace('\ufb01', 'fi')
        return title, text

    def get_corpus(self, url):
        self.title, text = self.copy_article(url)

        self.corpus = text.split('\n')    #['en', 'en'...]のリスト
        tmp_corpus = self.corpus.copy()
        self.remove_image_sentence(tmp_corpus)      # 翻訳用のcorpusから画像テキストを抽出, 除外
        self.remove_references_sentence(tmp_corpus) # 翻訳用のcorpusからReferencesを抽出, 除外
        tmp_corpus.append(self.title)
        print("size: ", len(tmp_corpus))

        # ['text1', 'text2'..., 'title']
        return tmp_corpus

    def remove_image_sentence(self, tmp_corpus):
        # 翻訳の邪魔なので画像を除外
        self.img_list = []
        for sentence in self.corpus:
            if re.match('<img title=.*>', sentence):
                self.img_list.append(sentence)
                tmp_corpus.remove(sentence) 

    def add_image_sentence_in_directory(self, dir):
        for img_sentence in self.img_list:
            dir[img_sentence] = img_sentence
     
    def remove_references_sentence(self, tmp_corpus):
       # 翻訳の邪魔なのでreferencesを除外
        self.ref_list = []
        is_ref = False
        for sentence in self.corpus:
            if is_ref:
                self.ref_list.append(sentence)
                tmp_corpus.remove(sentence)
            if re.match('# References', sentence):
                is_ref = True

    def add_references_sentence_in_directory(self, dir):
        for ref_sentence in self.ref_list:
            dir[ref_sentence] = ref_sentence

    def close_driver(self):
        self.driver.close()
