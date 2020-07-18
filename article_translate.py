import sys
from kibela_selenium.kibela import KibelaDriver
from deepL_selenium.deepL import DeepLDriver

if __name__ == '__main__':

    kibela_url = 'https://hidaka.kibe.la'#/groups/2'
    password = sys.argv[1]

    my_driver_path = 'C:/Users/SGRSN/Desktop/chromedriver_win32/chromedriver'

    # kibrlaにログイン
    my_kibela = KibelaDriver(kibela_url, 'sgrsn1711@gmail.com', password, my_driver_path)

    # kibelaから記事をコピー
    article_url = 'https://hidaka.kibe.la/notes/142'
    tmp_corpus = my_kibela.get_corpus(article_url)

    # deepLで翻訳
    my_deepL = DeepLDriver(driver_path=my_driver_path)
    my_deepL.run_translation(corpus=tmp_corpus, time_to_translate=25, destination_language='ja',
                          load_and_store_at=None, quit_web=False, raise_error=True)
    my_deepL.close_driver()

    # kibelaに翻訳結果を書き込み
    translation = my_deepL.get_translated_corpus() # {'en': 'ja', ...}の辞書型
    ja_title, ja_text = my_kibela.get_translated(translation)
    my_kibela.write_article(ja_title, ja_text, pub=False)
    #my_kibela.close()
