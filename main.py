from scrap_bk import ScrapyBook
import warnings

warnings.filterwarnings('ignore')
import pickle

if __name__ == '__main__':
    s = ScrapyBook('健康')
    books_ls = s.request()

