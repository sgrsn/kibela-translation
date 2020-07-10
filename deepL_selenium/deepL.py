import os
import json
import time
import random

import pyperclip as clipboard

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

class DeepLDriver():

    def __init__(self, destination_language='ja', driver_path='chromedriver'):

        self.driver_path = driver_path
        self.driver = webdriver.Chrome(self.driver_path)

        self.translations = {}
        
        self.default_url='https://www.deepl.com/<lang>/translator'
        self.destination_language = destination_language
        self.available_languages = ['fr', 'en', 'de', 'es', 'pt', 'it', 'nl', 'pl', 'ru', 'ja', 'zh']

        if self.destination_language in self.available_languages:
            self.url = self.default_url.replace('<lang>', self.destination_language)
        
        else:
            print("対応していない言語です : ", self.destination_language)

        self.driver.get(self.url)
        time.sleep(1.0)

    def scroll_to_element(self, elmt, sleep=1):

        y = elmt.location['y']
        y = y - 150
        self.driver.execute_script("window.scrollTo(0, {})".format(y))
        time.sleep(sleep)

    def close_driver(self):
        self.driver.quit()

    def add_source_text(self, sentence):

        clipboard.copy(sentence)
        input_css = 'div.lmt__inner_textarea_container textarea'
        input_area = self.driver.find_element_by_css_selector(input_css)
        
        input_area.clear() # self.sleep(1)
        input_area.send_keys(Keys.CONTROL, "v")

    def get_translation_copy_button(self):

        button_css = ' div.lmt__target_toolbar__copy button' 
        button = self.driver.find_element_by_css_selector(button_css)
        # attribute "_dl-attr should be onClick: $0.doCopy"
        return button

    def get_translation(self, step_time_click=5.0, limit_time=50.0):
        
        button = self.get_translation_copy_button()
        content = ""
        clipboard.copy("")
        wait_counter = 0.0
        while True:
            print("wait...")
            time.sleep(step_time_click)
            wait_counter += step_time_click

            self.scroll_to_element(button)
            try:
                button.click()
            except:
                pass
            
            content = clipboard.paste()

            if len(content) > 0:
                print("翻訳確認")
                break

            if wait_counter > limit_time:
                print("翻訳失敗, DeepLからコピーできませんでした")

        return content

    def load_translations(self, file_path):

        # Checking translation existence
        if not os.path.exists(file_path):
            return

        # If exists loading it
        with open(file_path) as jfile:
            existing_translations = json.load(jfile)
        
        # And storring in translated corpus
        for original, translation in existing_translations.items():
            self.translations[original]=translation
     

    def prepare_batch_corpus(self, corpus, joiner, max_caracter=4900):
        
        # Size information
        nb_sentence = len(corpus)
    
        # Batch information (reset these values after each batch finalization)
        batch = []
        batch_corpus = []
        batch_length = 0
                
        # Flag used in case of a last sentence which is already translated
        erase_last_sentence = False

        # Going throug each sentence of the initial corpus to create the batches
        for idx, sentence in enumerate(corpus):

            last_sentence = idx + 1 == nb_sentence

            # Check sentence size
            if len(sentence)> max_caracter:
                # TODO : split too big sentences on '\n', translate separated parts and reconciliate them.
                raise

            # Don't add to batch if sentence already traducted
            if sentence in self.translations.keys():
                # self.print_translation(sentence, self.translations[sentence])
                if not last_sentence: continue
                erase_last_sentence = True

            # Don't add to batch if sentence already in batch
            if sentence in batch:
                if not last_sentence: continue
                erase_last_sentence = True

            # Checking the batch size before adding a new sentence in it
            hypothetical_length = batch_length + len(sentence)
            if hypothetical_length < max_caracter:
                if not erase_last_sentence:
                    batch.append(sentence)
                    batch_length += len(sentence) + len(joiner)
                if not last_sentence: continue
                
            # Finalizing batch beforee storing
            joined_batch = joiner.join(batch)
            joined_batch_size = len(joined_batch)

            assert joined_batch_size < max_caracter, "Batch size size is too long for DeepL : {}".format(max_caracter)

            # Do not add an empty batch
            if joined_batch_size == 0:
                continue

            # Save batch in the corpus
            batch_corpus.append({
                'text':joined_batch,
                'size':len(batch),
                'joiner':joiner,
                'original_batch':batch
            })
            
            batch = [sentence]
            batch_length = len(sentence) + len(joiner)
                       
        return batch_corpus


    def translation_process(self, corpus_batch, time_to_translate, time_batch_rest):

        nb_batch = len(corpus_batch)

        # 5000文字づつ分けて処理
        for idx_batch, batch in enumerate(corpus_batch):

            print('({}/{}) - nb translation iteration.'.format(idx_batch+1, nb_batch))

            self.add_source_text(batch['text']) # DeepLに貼り付け
            
            print('Waiting for translation')
        
            full_translation = self.get_translation()
            separate = full_translation.split(batch['joiner'])
        
            assertion_message = 'The number of sentences in the translation does not match the original number of sentences'
            assert len(separate)==batch['size'], assertion_message
            # Solution could be : 1) Use another joiner 2) not to use batches

            for idx_trad, sentence in enumerate(batch['original_batch']):
                translation = separate[idx_trad]
                self.translations[sentence] = translation
                # self.print_translation(sentence, translation)
                
            time.sleep(time_batch_rest)

    def run_translation(
        self, corpus='Hello, World!', destination_language='en', joiner='\r\n____\r\n', quit_web=True, 
        time_to_translate=10, time_batch_rest=2, raise_error=False,
        load_at=None, store_at=None ,load_and_store_at=None):

        # Check corpus format
        if type(corpus)==str:
            corpus = [corpus]

        # Eventually load translation
        if load_and_store_at:
            load_at, store_at = load_and_store_at, load_and_store_at
        if load_at:
            self.load_translations(file_path=load_at)
        
        # Prepare batched corpus
        corpus_batch = self.prepare_batch_corpus(corpus, joiner)
        
        # Check data to translate
        if len(corpus_batch)==0:
            self.add_source_text('No data to translate. Closing window.')
            time.sleep(1.0)
            return
            
        # Check destination language
        if destination_language!=self.destination_language:
            self.destination_language = destination_language
            self.set_url()
            self.load_url()

        # MAKE TRANSLATION ON DEEPL WITH CORPUS BATCHED
        try:
            self.translation_process(corpus_batch, time_to_translate, time_batch_rest)
        
        # Dealing with error if one occurring during translation process
        except:
            store_at = 'translation_error.json' if store_at is None else store_at.replace('.json', '_error.json')
            self.close_driver()
            # self.print_translation_error(store_at)        
            if raise_error:
                self.save_translations(file_path=store_at)
                raise

        # Eventually store translation
        if store_at:
            self.save_translations(file_path=store_at)
        
        # Close the driver session if necessary
        if quit_web:
            self.close_driver()

    def get_translated_corpus(self):

        return self.translations
