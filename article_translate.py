import sys
from kibela_selenium.kibela import KibelaDriver
from deepL_selenium.deepL import DeepLDriver

if __name__ == '__main__':

    # kibelaのチームのURL(ログイン用)
    kibela_url = 'https://hidaka.kibe.la/groups/2'

    # 翻訳する記事のURL
    article_url = 'https://hidaka.kibe.la/notes/142'

    your_id = sys.argv[1]
    your_password = sys.argv[2]

    my_driver_path = 'C:/Users/i7-860/OneDrive/デスクトップ/chromedriver_win32/chromedriver'

    # kibrlaにログイン
    my_kibela = KibelaDriver(kibela_url, your_id, your_password, my_driver_path)

    # kibelaから記事をコピー
    tmp_corpus = my_kibela.get_corpus(article_url)

    # deepLで翻訳
    my_deepL = DeepLDriver(driver_path=my_driver_path)
    my_deepL.run_translation(corpus=tmp_corpus, time_to_translate=25, destination_language='ja',
                          load_and_store_at=None, quit_web=False, raise_error=True)
    my_deepL.close_driver()

    # kibelaに翻訳結果を書き込み
    translation = my_deepL.get_translated_corpus()
    ja_title, ja_text = my_kibela.get_translated(translation)
    my_kibela.write_article(ja_title, ja_text, pub=False)
    #my_kibela.close()
