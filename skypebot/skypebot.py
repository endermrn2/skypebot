import re
from datetime import datetime, timedelta, timezone

from actions import cama
from actions import coin
from actions import fujam
from actions import hola
from actions.dict import dict
from actions.ista import ista
from actions.ponto import ponto


KEYWORDS = {
    'help': ('@ro help', '<at id="8:live:976d89d0eaa03977">Ro</at> help'),
    'fujam': ('fujam', '#fujam', 'fujam para as colinas'),
    'commit': ('#commit',),
    'hola': ('#hola',),
    'coin': ('rb©oin', 'rb©'),
    'lunch': ('#almoco', '#almoço', '#lunch'),
}
BRAZIL_TIMEZONE = timezone(-timedelta(hours=3), 'Brazil')


def handle(event):
    message = event.msg.content.lower()

    coin.coin(event)

    keywords_mapping = (
        (_ponto, message.startswith('ponto')),
        (_ista, message.endswith('ista')),
        (_pregunton, message.endswith('???')),
        (_radical, 'é disso que eu gosto' in message),
        (_radical, 'é disso q eu gosto' in message),
        (_piorou, 'tava ruim' in message),
        (_piorou, 'tava meio ruim' in message),
        (_dict, '#dict' in message),
        (_coin, message in KEYWORDS['coin']),
        (_help, message in KEYWORDS['help']),
        (_fujam, message in KEYWORDS['fujam']),
        (_commit, message in KEYWORDS['commit']),
        (_hola, message in KEYWORDS['hola']),
        (_lunch, message in KEYWORDS['lunch']),
    )

    for function, match in keywords_mapping:
        if match:
            event.msg.chat.setTyping()
            function(event)
            break


def _radical(event):
    event.msg.chat.sendMsg('RADICAAAAL!!!')


def _help(event):
    help = """
    - ? - Amigo pregunton (mariachilove)
    - #commit - #CAMA
    - #hola - Hola
    - ponto {chegada} {?saida_intervalo},{volta_intervalo?} {?horas a trabalhar?} - ponto
    - #ista - ista
    """
    event.msg.chat.sendMsg(help)


def _ista(event):
    event.msg.chat.sendMsg(ista())


def _fujam(event):
    event.msg.chat.sendMsg(fujam.switch_two())


def _piorou(event):
    event.msg.chat.sendMsg('agora parece q piorou')


def _pregunton(event):
    event.msg.chat.sendMsg('AAAAAAAAH QUE AMIGO TAN PREGUNTON!!!')
    event.msg.chat.sendMsg('(mariachilove)')


def _commit(event):
    cama.main(event.msg.chat.sendMsg)


def _hola(event):
    event.msg.chat.sendMsg(hola.main(event.msg.user.name.first))


def _ponto(event):
    params = event.msg.content.split(' ')
    horario = params[1]
    rest_hours = params[2] if len(params) > 2 else '1:00'
    working = params[3] if len(params) > 3 else '8:30'
    event.msg.chat.sendMsg(ponto(horario, working, rest_hours))


def _dict(event):
    regex_pattern = '</legacyquote>([a-záàâãéèêíïóôõöúç]*)<legacyquote>'
    msg = event.msg.content.lower()

    word = re.findall(regex_pattern, msg)[0]
    try:
        event.msg.chat.sendMsg('{}\n{}'.format(*dict(word)))
    except IndexError:
        event.msg.chat.sendMsg('Não achei essa palavra: {}'.format(word))


def _coin(event):
    coin.status(event)


def _lunch(event):
    now = datetime.now(tz=BRAZIL_TIMEZONE)
    lunch_time = now.replace(hour=11, minute=30)

    if now == lunch_time:
        event.msg.chat.sendMsg('#PartiuAlmoço')
        return
    elif now > lunch_time:
        # Tomorrow lunch
        lunch_time += timedelta(days=1)

    seconds_left = (lunch_time - now).seconds
    minutes, seconds = divmod(seconds_left, 60)
    hours, minutes = divmod(minutes, 60)
    msg = 'Faltam {}h{}min para o almoço'.format(hours, minutes)
    event.msg.chat.sendMsg(msg)
