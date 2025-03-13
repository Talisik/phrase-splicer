import pykakasi
from fun_things import lazy
import uroman


@lazy.fn
def kks():
    return pykakasi.kakasi()


@lazy.fn
def ur():
    return uroman.Uroman()
