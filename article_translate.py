if __name__ == '__main__':
    kibela_url = 'https://hidaka.kibe.la'#/groups/2'
    my_kibela = KibelaDriver(kibela_url, 'sgrsn1711@gmail.com', 'HidakaKB1711')
    #article = my_kibela.copy_article('https://hidaka.kibe.la/notes/101')
    article_url = 'https://hidaka.kibe.la/notes/142'
    article = my_kibela.copy_article(article_url)
    my_corpus = article['text'].split('\n')    #['en', 'en'...]のリスト

    tmp_corpus = my_corpus.copy()

    # 翻訳の邪魔なので画像を除外
    img_list = []
    for sentence in my_corpus:
        if re.match('<img title=.*>', sentence):
            img_list.append(sentence)
            tmp_corpus.remove(sentence)

    tmp_corpus.append(article['title'])
    print("size: ", len(tmp_corpus))
    
    # Create translation object
    my_driver_path = 'C:\\Users\\i7-860\\OneDrive\\デスクトップ\\chromedriver_win32\\chromedriver'
    deepL = seleniumDeepL(driver_path=my_driver_path, loglevel='info')

    deepL.run_translation(corpus=tmp_corpus, time_to_translate=25, destination_language='ja',
                          load_and_store_at=None, quit_web=False, raise_error=True)
    deepL.close_driver()

    translation = deepL.get_translated_corpus() # {'en': 'ja', ...}の辞書型
    ja_text_list = []
    ja_title = translation[ article['title'] ]

    # 画像を辞書に追加
    for img_sentence in img_list:
        translation[img_sentence] = img_sentence

    for i, en_text in enumerate(my_corpus):

        if en_text in translation:
            ja_text_list.append( translation[en_text] ) 

        else:
            print('keyがないですね')
            print('key: ', en_text)
            
    ja_texts = '\n'.join(ja_text_list)
    my_kibela.write_article(ja_title, ja_texts, pub=False)
    #my_kibela.close()
