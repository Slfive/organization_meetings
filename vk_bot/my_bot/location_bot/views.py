"""Handlers for bot and cartGenerate"""

from __future__ import unicode_literals
import random
import json
import vk
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from location_bot.models import VK_sender
from location_bot.buttons import text_button, location_button
from location_bot.bot_config import TOKEN as token, CONFIRMATION_TOKEN as confirmation_token, SECRET_KEY as secret_key

class MessageView(APIView):
    """API class for get meet coordinates in second type"""
    def post(self, request):
        """Method post for save obj with meet coordinates"""
        messages = VK_sender.objects.all()
        message_meet = request.data['data']
        message = VK_sender(user_id=messages[0].user_id,
                            coor_x=str(message_meet['coor_x']),
                            coor_y=str(message_meet['coor_y']),
                            text=str(message_meet['text']),
                            key_phrase=str(messages[len(messages)-1].key_phrase),
                            type=messages[len(messages)-1].type,
                            count=messages[len(messages)-1].count + 1)
        message.save()
        return Response({'success': message.count})

@csrf_exempt
def index(request):
    """Handler for bot"""
    if request.method == "POST":
        data = json.loads(request.body)# take POST request from auto-generate variable
                                       # <request.body> in json format
        if data['secret'] == secret_key:
            if data['type'] == 'confirmation':
                return HttpResponse(confirmation_token, content_type="text/plain", status=200)
            elif data['type'] == 'message_new':# if VK server send a message
                session = vk.Session()
                api = vk.API(session, v=5.107)
                vk_link = 'https://vk.com/eugenef12'
                vk_friend_link = ''
                keyboards = [0]*2
                keyboards[0] = {
                    "one_time": True,
                    "buttons":[
                        [text_button(label='Знаю место и хочу назначить там встречу',
                                     color='positive')],
                        [text_button(label='Еще не определился с выбором места',
                                     color='positive')]
                    ]
                }
                keyboards[1] = {
                    "one_time": True,
                    "buttons":[
                        [location_button()],
                    ]
                }
                for i in range(len(keyboards)):
                    keyboards[i] = json.dumps(keyboards[i], ensure_ascii=False).encode('utf-8')
                    keyboards[i] = str(keyboards[i].decode('utf-8'))
                user_id = data['object']['message']['from_id']
                text = data['object']['message']['text']
                sender = VK_sender()
                sender.user_id = user_id
                sender.count = 0
                messages = VK_sender.objects.all()
                last_message = 0
                if len(messages) != 0:
                    last_message = messages[len(messages) - 1]
                if text == "delete":
                    VK_sender.objects.all().delete()
                ans_1 = 'Знаю место и хочу назначить там встречу'
                ans_2 = 'Еще не определился с выбором места'

                if len(messages) == 0 and text == "Начать":
                    sender.text = text
                    sender.type = 3
                    sender.coor_x = '-1'
                    sender.coor_y = '-1'
                    sender.count = 0

                    sender.key_phrase = ''
                    sender.save()
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Привет! Хочешь устроить встречу с другом"
                                      "? Напиши боту 'Хочу встречу'. Если в "
                                      "какой-то момент тебе не захочется продолжать, "
                                      "напиши команду delete, и вся история сотрётся.",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)
                elif last_message == 0 and text != "Начать":
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Хей, напиши 'Начать' для старта. Давай ка ещё раз",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)

                if len(messages) == 1 and text == "Хочу встречу":
                    sender.text = text
                    sender.type = 3
                    sender.coor_x = '-1'
                    sender.coor_y = '-1'
                    sender.count = 1
                    sender.key_phrase = ''
                    sender.save()
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Как ты хочешь встретиться?",
                                      random_id=random.randrange(-5000000, 5000000),
                                      v=5.107, keyboard=keyboards[0])
                elif len(messages) == 1 and text != "Хочу встречу":
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Хей, я просил написать 'Хочу встречу'. "
                                      "Давай ка ещё раз",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)

                if last_message.count == 1 and text == ans_1:
                    sender.text = text
                    sender.type = 1
                    sender.coor_x = '-1'
                    sender.coor_y = '-1'
                    sender.count = last_message.count + 1
                    sender.key_phrase = ''
                    sender.save()
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Отметь своё местоположение:",
                                      random_id=random.randrange(-5000000, 5000000),
                                      v=5.107, keyboard=keyboards[1])
                elif last_message.count == 1 and text == ans_2:
                    sender.text = text
                    sender.type = 2
                    sender.coor_x = '-1'
                    sender.coor_y = '-1'
                    sender.count = last_message.count + 1
                    sender.key_phrase = ''
                    sender.save()
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Отметь своё местоположение на карте",
                                      random_id=random.randrange(-5000000, 5000000),
                                      v=5.107, keyboard=keyboards[1])
                elif last_message.count == 1 and text != ans_1 and text != ans_2:
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Хей, я просил выбрать одно из двух."
                                      " Давай ка ещё раз",
                                      random_id=random.randrange(-5000000, 5000000),
                                      v=5.107, keyboard=keyboards[0])

                if last_message.count == 2 and text == "" and last_message.type == 1:
                    sender.text = str(data['object']['message']['geo']['coordinates']['latitude'])
                    sender.text += ' '
                    sender.text += str(data['object']['message']['geo']['coordinates']['longitude'])
                    sender.type = 1
                    sender.key_phrase = ''
                    sender.coor_x = data['object']['message']['geo']['coordinates']['latitude']
                    sender.coor_y = data['object']['message']['geo']['coordinates']['longitude']
                    sender.count = last_message.count + 1
                    sender.save()
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Отлично! Теперь отметь место встречи",
                                      random_id=random.randrange(-5000000, 5000000),
                                      v=5.107, keyboard=keyboards[1])
                elif last_message.count == 2 and text == "" and last_message.type == 2:
                    sender.type = 2
                    sender.text = str(data['object']['message']['geo']['coordinates']['latitude'])
                    sender.text += ' '
                    sender.text += str(data['object']['message']['geo']['coordinates']['longitude'])
                    sender.coor_x = data['object']['message']['geo']['coordinates']['latitude']
                    sender.coor_y = data['object']['message']['geo']['coordinates']['longitude']
                    sender.key_phrase = ''
                    sender.count = last_message.count + 1
                    sender.save()
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Отлично, теперь подумай и скажи,"
                                      " в месте какого типа ты бы хотел встретится "
                                      "(это может быть как просто кафе или парк, "
                                      "так и фраза, рода 'где поесть')",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)
                elif last_message.count == 2 and text != "" and last_message.type == 1:
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Хей, я просил отметить себя на карте. "
                                      "Давай ещё раз",
                                      random_id=random.randrange(-5000000, 5000000),
                                      v=5.107, keyboard=keyboards[1])
                elif last_message.count == 2 and text != "" and last_message.type == 2:
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Хей, я же просил отметить своё местоположение"
                                      "на карте. Давай ка ещё раз",
                                      random_id=random.randrange(-5000000, 5000000),
                                      v=5.107, keyboard=keyboards[1])

                if last_message.count == 3 and text == "" and last_message.type == 1:
                    sender.text = ''
                    sender.type = 1
                    sender.coor_x = data['object']['message']['geo']['coordinates']['latitude']
                    sender.coor_y = data['object']['message']['geo']['coordinates']['longitude']
                    sender.count = last_message.count + 1
                    sender.key_phrase = last_message.key_phrase
                    sender.save()
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Отлично! Теперь отправь ссылку на своего друга",
                                      random_id=random.randrange(-5000000, 5000000),
                                      v=5.107)
                elif last_message.count == 3 and text != "" and last_message.type == 1:
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Хей, я просил отметить место встречи."
                                      " Давай ещё раз",
                                      random_id=random.randrange(-5000000, 5000000),
                                      v=5.107, keyboard=keyboards[1])
                elif last_message.count == 3 and last_message.type == 2:
                    sender.text = text
                    sender.type = 2
                    sender.coor_x = '-1'
                    sender.coor_y = '-1'
                    sender.count = last_message.count + 1
                    sender.key_phrase = text
                    sender.save()
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="А теперь введи ссылку на своего друга, "
                                      "с которым ты планируешь встречаться",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)

                if last_message.count == 4 and text[:15] == vk_link[:15] and last_message.type == 1:
                    vk_friend_link = text[15:]
                    friends_massiv = api.users.get(access_token=token,
                                                   user_ids=vk_friend_link,
                                                   v=5.107)
                    friend_id = friends_massiv[0]['id']
                    api.messages.send(access_token=token, user_id=str(friend_id),
                                      message="Привет! С тобой хочет встретится https://vk.com/id"
                                      + str(user_id)
                                      + "\n Напиши 'Встретиться', если готов встретится "
                                      " или напиши 'Отказ от встречи', если отказываешься",
                                      random_id=random.randrange(-500000, 500000), v=5.107)
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Приглашение отправлено!",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)
                    sender.text = text
                    sender.type = 1
                    sender.coor_x = '-1'
                    sender.coor_y = '-1'
                    sender.count = last_message.count + 1
                    sender.key_phrase = last_message.key_phrase
                    sender.save()
                elif last_message.count == 4 and text[:15] != vk_link[:15] and last_message.type == 1:
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Хей, это не ссылка. Давай ка ещё раз, только ссылку",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)
                elif last_message.count == 4 and text[:15] == vk_link[:15] and last_message.type == 2:
                    vk_friend_link = text[15:]
                    friend_massiv = api.users.get(access_token=token,
                                                  user_ids=vk_friend_link,
                                                  v=5.107)
                    friend_id = friend_massiv[0]['id']
                    api.messages.send(access_token=token, user_id=str(friend_id),
                                      message="Привет! с тобой хочет встретиться https://vk.com/id"
                                      + str(user_id) +
                                      "\n Он, не знает где, но будет искать по фразе "
                                      + last_message.key_phrase +
                                      "\n Напиши 'Встретиться', если готов встретиться, "
                                      "или напиши 'Отказ от встречи', если отказываешь",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Ждите, пока друг подтвердит встречу "
                                      "и отметит себя на карте",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)
                    sender.text = text
                    sender.type = 2
                    sender.coor_x = '-1'
                    sender.coor_y = '-1'
                    sender.count = last_message.count + 1
                    sender.key_phrase = last_message.key_phrase
                    sender.save()
                elif last_message.count == 4 and text[:15] != vk_link[:15] and last_message.type == 2:
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Хей, это явно не ссылка, давай ещё раз",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)

                if last_message.count == 5 and text == "Встретиться":
                    sender.text = text
                    if last_message.type == 1:
                        sender.type = 1
                    else:
                        sender.type = 2
                    sender.coor_x = '-1'
                    sender.coor_y = '-1'
                    sender.count = last_message.count + 1
                    sender.key_phrase = last_message.key_phrase
                    sender.save()
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Отметь себя на карте",
                                      random_id=random.randrange(-5000000, 5000000),
                                      v=5.107, keyboard=keyboards[1])

                elif last_message.count == 5 and text == "Отказ от встречи":
                    api.messages.send(access_token=token,
                                      user_id=messages[len(messages)-1].user_id,
                                      message="Ваш друг не хочет встречаться сейчас, "
                                      " попробуйте позже",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)
                    VK_sender.objects.all().delete()
                elif last_message.count == 5 and text != "Встретиться":
                    api.messages.send(access_token=token, user_id=user_id,
                                      message="Хей, я просил написать 'Встретиться' или"
                                      " 'Отказ от встречи'. Давай ещё раз",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)

                if last_message.count == 6 and text == "" and last_message.type == 1:
                    f_x = data['object']['message']['geo']['coordinates']['latitude']
                    f_y = data['object']['message']['geo']['coordinates']['longitude']
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Ссылка на маршрут: "
                                      "http://alice.dqpig.ml/cartGenerate/?f_x="
                                      + str(f_x) + "&f_y=" + str(f_y)
                                      + "&m_x=" + str(messages[len(messages)-3].coor_x)
                                      + "&m_y=" + str(messages[len(messages)-3].coor_y),
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)
                    api.messages.send(access_token=token,
                                      user_id=messages[len(messages)-3].user_id,
                                      message="Ссылка на маршру: "
                                      "http://alice.dqpig.ml/cartGenerate/?f_x="
                                      + str(messages[len(messages)-4].coor_x) + "&f_y="
                                      + str(messages[len(messages)-4].coor_y) + "&m_x="
                                      + str(messages[len(messages)-3].coor_x) + "&m_y="
                                      + str(messages[len(messages)-3].coor_y),
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)
                    VK_sender.objects.all().delete()
                elif last_message.count == 6 and text == "" and last_message.type == 2:
                    sender.type = 2
                    sender.text = str(data['object']['message']['geo']['coordinates']['latitude'])
                    sender.text += ' '
                    sender.text += str(data['object']['message']['geo']['coordinates']['longitude'])
                    sender.coor_x = data['object']['message']['geo']['coordinates']['latitude']
                    sender.coor_y = data['object']['message']['geo']['coordinates']['longitude']
                    sender.key_phrase = last_message.key_phrase
                    sender.count = last_message.count + 1
                    sender.save()
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Ждите, пока организатор выберет место встречи",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)
                    api.messages.send(access_token=token,
                                      user_id=messages[3].user_id,
                                      message="Ссылка на страницу выбора места встречи: "
                                      "http://alice.dqpig.ml/generate_meet_point/"
                                      "\n Вы можете выбрать любую точку на карте, но на ней заранее"
                                      " отмечены точки, которые подходят под ваш запрос и лежат"
                                      " в окружности, центр которой - середина отрезка между вами"
                                      "\n Как будете готовы - напишите 'готов'",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)
                elif last_message.count == 6 and text != "":
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Хей, я просил отметить себя на карте"
                                      ". Давай ещё раз",
                                      random_id=random.randrange(-5000000, 5000000),
                                      v=5.107, keyboard=keyboards[1])

                if last_message.count == 7:
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Место встречи ещё не выбрно",
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)

                # 7 have message, where friend marked himself in map, and 8 have message,
                # where we can see meet coords
                if last_message.count == 8 and text == "готов":
                    m_x = messages[len(messages)-1].coor_x
                    m_y = messages[len(messages)-1].coor_y
                    api.messages.send(access_token=token, user_id=str(user_id),
                                      message="Ссылка: http://alice.dqpig.ml/cartGenerate/?f_x="
                                      + str(messages[3].coor_x) +
                                      "&f_y=" + str(messages[3].coor_y) +
                                      "&m_x=" + str(m_x) + "&m_y=" + str(m_y),
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)
                    print('ok')
                    api.messages.send(access_token=token,
                                      user_id=messages[len(messages)-1].user_id,
                                      message="Ссылка: http://alice.dqpig.ml/cartGenerate/?f_x="
                                      + str(messages[7].coor_x) +
                                      "&f_y=" + str(messages[7].coor_y) +
                                      "&m_x=" + str(m_x) + "&m_y=" + str(m_y),
                                      random_id=random.randrange(-5000000, 5000000), v=5.107)
                    VK_sender.objects.all().delete()
                else:
                    api.message.send(access_token=token, user_id=str(user_id),
                                     message="Хей, ты либо напиши 'готов', либо иди выбирай",
                                     random_id=random.randrange(-5000000, 5000000), v=5.107)

                return HttpResponse('ok', content_type="text/plain", status=200)
            #else:
                #raise Http404
    else:
        return HttpResponse('see you :)')


def cart_generate(request):
    """Handler for page, where generate map for users"""

    context = {
        "f_x": request.GET.get("f_x"),
        "f_y": request.GET.get("f_y"),
        "m_x": request.GET.get("m_x"),
        "m_y": request.GET.get("m_y")
    }

    return render(request, "cart_generate.html", context)


def generate_meet_point(request):
    """Handler for page, where user select meet point"""

    messages = VK_sender.objects.all()
    context = {
        "keyPhrase": str(messages[len(messages) - 1].key_phrase),
        "f_x": str(messages[3].coor_x),
        "f_y": str(messages[3].coor_y),
        "s_x": str(messages[len(messages) - 1].coor_x),
        "s_y": str(messages[len(messages) - 1].coor_y)
    }
    return render(request, "generate_meet_point.html", context)
