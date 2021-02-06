#!/usr/bin/env python
# coding: utf-8

# # Выявление определяющих успешность игры закономерностей 

# Мы работаем в интернет-магазине «Стримчик», который продаёт по всему миру компьютерные игры. Из открытых источников доступны исторические данные о продажах игр, оценки пользователей и экспертов, жанры и платформы (например, Xbox или PlayStation). Нам нужно выявить определяющие успешность игры закономерности. Это позволит сделать ставку на потенциально популярный продукт и спланировать рекламные кампании.
# 
# Перед нами данные до 2016 года. Представим, что сейчас декабрь 2016 г., и мы планируете кампанию на 2017-й. Нужно отработать принцип работы с данными. 
# 
# В наборе данных попадается аббревиатура ESRB (Entertainment Software Rating Board) — это ассоциация, определяющая возрастной рейтинг компьютерных игр. ESRB оценивает игровой контент и присваивает ему подходящую возрастную категорию, например, «Для взрослых», «Для детей младшего возраста» или «Для подростков».

# #### Описание данных
# - Name — название игры
# - Platform — платформа
# - Year_of_Release — год выпуска
# - Genre — жанр игры
# - NA_sales — продажи в Северной Америке (миллионы проданных копий)
# - EU_sales — продажи в Европе (миллионы проданных копий)
# - JP_sales — продажи в Японии (миллионы проданных копий)
# - Other_sales — продажи в других странах (миллионы проданных копий)
# - Critic_Score — оценка критиков (максимум 100)
# - User_Score — оценка пользователей (максимум 10)
# - Rating — рейтинг от организации ESRB (англ. Entertainment Software Rating Board). Эта ассоциация определяет рейтинг компьютерных игр и присваивает им подходящую возрастную категорию.

# #### План работы 
# - Шаг 1. Изучение общей информации
# - Шаг 2. Подготовка данных
#   - Замена названий столбцов;
#   - Преобразование данных в нужные типы;
#   - Обработка пропусков при необходимости;
#   - Исправление ошибок
# - Шаг 3. Исследовательский анализ данных
#   - Сколько игр выпускалось в разные годы? Важны ли данные за все периоды?
#   - Как менялись продажи по платформам? За какой характерный срок появляются новые и исчезают старые платформы?
#   - Возьмем данные за соответствующий актуальный период. 
#   - Какие платформы лидируют по продажам, растут или падают? 
#   - Построим график «ящик с усами» по глобальным продажам игр в разбивке по платформам. 
#   - Как влияют на продажи внутри одной популярной платформы отзывы пользователей и критиков? 
#   - Соотнесем выводы с продажами игр на других платформах.
#   - Посмотрим на общее распределение игр по жанрам. Что можно сказать о самых прибыльных жанрах? Выделяются ли жанры с высокими и низкими продажами?
# - Шаг 4. Портрет пользователя каждого региона
# 
#  Определим для пользователя каждого региона (NA, EU, JP):
#   - Самые популярные платформы (топ-5). 
#   - Самые популярные жанры (топ-5). 
#   - Влияет ли рейтинг ESRB на продажи в отдельном регионе?
# - Шаг 5. Проверка гипотез
#   - Средние пользовательские рейтинги платформ Xbox One и PC одинаковые;
#   - Средние пользовательские рейтинги жанров Action (англ. «действие», экшен-игры) и Sports (англ. «спортивные соревнования») разные.
# 
# - Шаг 6. Общий вывод

# ## Шаг 1. Изучение общей информации 
# Откроем файл, посмотрим, что же там есть 

# In[69]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats as st


# In[4]:


games_data = pd.read_csv('datasets/games.csv')
print(games_data.info())


# In[5]:


display(games_data.head())


# В датасете 16715 строк, есть пропущенные значения. Критичные пропущенные значения - в столбце с годом выпуска, их меньше 2%, предлагаю эти строки просто удалить. Остальные пропуски оставить 
# 
# Нужно изменить некоторые типы данных (год выпуска) и изменить названия столбцов для более удобной работы с ними

# ## Шаг 2. Подготовка данных

# Приведем названия столбцов к более удобному для работы виду

# In[6]:


games_data.columns = games_data.columns.str.lower()


# In[7]:


print(games_data.info())


# Получилось 
# 
# Теперь перейдем к пропускам. Удалим строки с пропусками в стобце с годом выпуска 

# In[8]:


games_data.dropna(subset = ['year_of_release'], inplace = True)


# И займемся типами данных

# In[9]:


games_data['year_of_release'] = games_data['year_of_release'].astype('int')


# Добавим столбец с сумарными продажами по миру 
# 

# In[10]:


games_data['total_sales'] = games_data['na_sales'] + games_data['eu_sales'] + games_data['jp_sales'] + games_data['other_sales']


# Заменим значения отзывов tbd (неопределено) на NaN

# In[11]:


def add_score(score):
    if score == 'tbd':
        score = 'NaN'
    return score


# In[12]:


games_data['user_score'] = games_data['user_score'].apply(add_score)


# In[13]:


games_data['user_score'] = games_data['user_score'].astype('float64')


# Пропуски в стоблбцах name и genre оставляем, так как в актуальном периоде 2011-2016гг этих пропусков нет 

# Данные подготовлены. Начнем анализ

# ## Шаг 3. Исследовалельский анализ данных

# ### Сколько игр выпускалось в разные годы? Важны ли данные за все периоды?

# In[14]:


games_release_pivot = games_data.pivot_table(index = 'year_of_release', values = 'na_sales', aggfunc = 'count')
games_release_pivot.columns = ['quantity']


# In[15]:


display(games_release_pivot)


# Посмотрим на график для наглядности

# In[17]:



with plt.style.context('seaborn-pastel'):
    plt.figure(figsize=(15,5))
    plt.title('Количество выпущенных игр 1986 - 2016 гг', alpha=0.5, color="k", fontsize=18, fontstyle="italic", fontweight="bold", linespacing=10)
    plt.xlabel('год')
    plt.ylabel('количество')
    plt.grid()
    plt.plot(games_release_pivot, color = 'r')
    plt.show()


# Больше 200 игр в год выпускали только начиная с 1995 года(из-за начала развития различных платформ для игр), но самый резкий подъем был в 2001 году. Рассмотрим только период с 2000-2015гг

# ### Как менялись продажи по платформам? За какой характерный срок появляются новые и исчезают старые платформы?

# In[18]:


games_platform_pivot = games_data.pivot_table(index = ['platform', 'year_of_release'], values = 'total_sales', aggfunc = 'sum')
games_platform_pivot = games_platform_pivot.reset_index()


# In[19]:


display(games_platform_pivot)


# 31 платформа за 37 лет.
# Посмотрим на общие продажи по платформам и выберем платфимы с самыми продаваемыми играми 

# In[20]:


games_platform_pivot_total = games_data.pivot_table(index = 'platform', values = 'total_sales', aggfunc = 'sum')
games_platform_pivot_total.columns = ['total_sales']
games_platform_pivot_total.sort_values('total_sales')


# Лидирует с большим отрывом PS2, за ней идет X360  и PS3. Посмотрим на распределение по годам 

# In[21]:


ps2_pivot = games_platform_pivot.loc[games_platform_pivot['platform'] == 'PS2'].pivot_table(index = 'year_of_release', values = 'total_sales', aggfunc = 'sum')
ps2_pivot.columns = ['total_sales']


# In[22]:


plt.figure(figsize=(15,5))
plt.title('Распределение продаж игр на PS2 по годам', alpha=0.5, color="k", fontsize=18, fontstyle="italic", fontweight="bold", linespacing=10)
plt.xlabel('год')
plt.ylabel('продажи, миллионы проданных копий')
plt.grid()
plt.plot(ps2_pivot, color = 'r')
plt.show()


# PS2 вышла в марте 200, продажи росли до 2004. Возможно, из-за выхода в 2005г Portable версии, или из-за появления x360

# In[23]:


x360_pivot = games_platform_pivot.loc[games_platform_pivot['platform'] == 'X360'].pivot_table(index = 'year_of_release', values = 'total_sales', aggfunc = 'sum')
x360_pivot.columns = ['total_sales']


# In[24]:


plt.figure(figsize=(15,5))
plt.title('Распределение продаж игр на X360 по годам', alpha=0.5, color="k", fontsize=18, fontstyle="italic", fontweight="bold", linespacing=10)
plt.xlabel('год')
plt.ylabel('продажи')
plt.grid()
plt.plot(x360_pivot, color = 'r')
plt.show()


# и сразу взглянем на пс3

# In[25]:


ps3_pivot = games_platform_pivot.loc[games_platform_pivot['platform'] == 'PS3'].pivot_table(index = 'year_of_release', values = 'total_sales', aggfunc = 'sum')
ps3_pivot.columns = ['total_sales']


# In[26]:


plt.figure(figsize=(15,5))
plt.title('Распределение продаж игр на PS3 по годам', alpha=0.5, color="k", fontsize=18, fontstyle="italic", fontweight="bold", linespacing=10)
plt.xlabel('год')
plt.ylabel('продажи')
plt.grid()
plt.plot(ps3_pivot, color = 'r')
plt.show()


# Платформы ps3 и x360 вышли в одно время, подъем и спад у них очень похож

# Судя по распределениям продаж игр на топ платформач можно сделать вывод о том, что с выходом новых платформ (раз в 5 лет), игры на старые теряют актуальность.
# 
# Объединив вывод по продажам и вывод по выходам новых игр, можно определить актуальный период. Нам нужно построить прогноз на 2017 год, поэтому будем брать период с 2011 года. На новой консоли игры актуальные еще в течение 10 лет, новая консоль выходит каждые 5 лет, поэтому возьмем период 2011 - 2016 гг

# In[27]:


games_data_actual = games_data.loc[games_data['year_of_release'] >= 2011]


# In[28]:


print(games_data_actual.info())


# Как и говорилось выше, пропуски в name и genre ушли :)

# ### Какие платформы лидируют по продажам, растут или падают? 

# In[29]:


games_actual_platform_pivot = games_data_actual.pivot_table(index = ('platform'), values = 'total_sales', aggfunc = 'sum')
games_actual_platform_pivot.columns = ['total_sales']
games_actual_platform_pivot = games_actual_platform_pivot.reset_index()


# In[30]:


display(games_actual_platform_pivot)


# In[33]:


plt.figure(figsize=(15,5))
plt.title('Продажи игр 2011 - 2016гг', alpha=0.5, color="k", fontsize=18, fontstyle="italic", fontweight="bold", linespacing=10)
plt.grid()
ax = sns.barplot(y = 'total_sales', x = 'platform',  data=games_actual_platform_pivot,)


# Определенно лидеры по продажам PS3 и X360. Но мы уже выяснили, что продажи игр на эти консоли падают, а продажи игр на PS уже совсем еле заметны
# 
# Посмотрим на рост/падение продаж по остальным консолям 
# 

# <div class="alert alert-success"> 
# <h2> Комментарии от ревьюера №1</h2>
#     
# У тебя очень симпатичные графики 👍
# </div>

# In[34]:


actual_sales_per_year = games_data_actual.pivot_table(index = 'year_of_release', columns = 'platform', values = 'total_sales', aggfunc = 'sum')


# In[35]:


display(actual_sales_per_year)


# In[36]:


actual_sales_per_year.plot(
    figsize = (15, 10), title = 'Продажи 2011 - 2016 гг', grid = True)


# Продажа игр по всем платформам падает.
# 
# 
# Возможно, по каким-то новым платформам пик еще не пройден. Возьмем за потенциально прибыльные платформы новые - PS4, XOne, WiiU, а также вечного PC 

# In[37]:


plt.figure(figsize=(15,10))
plt.title('Глобальные продажи игр в разбивке по платформам', alpha=0.5, color="k", fontsize=18, fontstyle="italic", fontweight="bold", linespacing=10)
plt.xlabel('платформа')
plt.ylabel('продажи, млн копий')
plt.grid()
sns.boxplot(data=actual_sales_per_year)
plt.show()


# PS4 лидер по медианным продажам. Следом идут PS3 и X360, которые уже теряют свою актуальность. Далее 3DS и XOne
# 
# Основываясь на исследовании платформ, можно сделать ставку на PS4, XOne, WiiU и 3DS

# ### Влияние отзывов критиков и покупателей на продажи
# 
# Разберем влияние отзывов на продажи на примере одной консоли. Посмотрим, на какой отзывов больше 

# In[38]:


display(games_data_actual.pivot_table(index = 'platform', values = ['critic_score', 'user_score'], aggfunc = 'count'))


# Больше всего отзывов на ПС3, но платформа "увядает", поэтому рассмотрим ПС4

# In[39]:


plt.figure(figsize=(18,7))
plt.title('Вляние отзывов критиков на продажи игр на PS4 (2011 - 2016гг)', alpha=0.5, color="k", fontsize=18, fontstyle="italic", fontweight="bold", linespacing=10)
plt.xlabel('рейтинг')
plt.ylabel('продажи, млн копий')
plt.scatter(x='critic_score', y="total_sales", data=games_data_actual.loc[games_data_actual['platform'] == 'PS4'], color = 'r', alpha = 0.5)
plt.show()


# In[40]:


print(games_data_actual.loc[games_data_actual['platform'] == 'PS4']['critic_score'].corr(games_data_actual.loc[games_data_actual['platform'] == 'PS4']['total_sales']))


# In[41]:



plt.figure(figsize=(18,7))
plt.title('Вляние отзывов игроков на продажи игр на PS4 (2011 - 2016гг)', alpha=0.5, color="k", fontsize=18, fontstyle="italic", fontweight="bold", linespacing=10)
plt.xlabel('рейтинг')
plt.ylabel('продажи, млн копий')
plt.scatter(x='user_score', y="total_sales", data=games_data_actual.loc[games_data_actual['platform'] == 'PS4'], color = 'r', alpha = 0.5)
plt.show()


# In[42]:


print(games_data_actual.loc[games_data_actual['platform'] == 'PS4']['user_score'].corr(games_data_actual.loc[games_data_actual['platform'] == 'PS4']['total_sales']))


# Если отзывы критиков хоть как-то влияют на продажи игр, то отзывы игроков обратно влияют на продажи игр (хоть и слабо) - то есть, чем ниже рейтинг, тем лучше продажи 
# 
# Посмотрим, как обстоят дела с продажами на другие платформы 

# In[43]:


for platform, group_data in games_data_actual.groupby('platform'):
    games_data_actual.plot(x = 'critic_score', y = 'total_sales', kind = 'scatter', title = platform, color = 'r', alpha = 0.5)
    print(platform, ' ', games_data_actual.loc[games_data_actual['platform'] == platform]['critic_score'].corr(games_data_actual.loc[games_data_actual['platform'] == platform]['total_sales']))


# In[44]:


for platform, group_data in games_data_actual.groupby('platform'):
    games_data_actual.plot(x = 'user_score', y = 'total_sales', kind = 'scatter', title = platform, color = 'r', alpha = 0.5)
    print(platform, ' ', games_data_actual.loc[games_data_actual['platform'] == platform]['user_score'].corr(games_data_actual.loc[games_data_actual['platform'] == platform]['total_sales']))


# На остальных платформах ситуация похожая - есть зависимость продаж от рейтинга критиков, в то время как продажи мало зависят, а то и обратно зависят от оценок игроков. Конечно, есть исключения - игры на 3DS и на WiiU лучше продаются с высокими оценками пользователей 

# ### Распределение по жанрам 
# 
# Посмотрим на медианные продажи игр по жанрам 

# In[45]:


genre_pivot = games_data_actual.pivot_table(index = 'genre', values = 'total_sales', aggfunc = 'median')
genre_pivot.columns = ['med_sales']
genre_pivot = genre_pivot.reset_index()


# In[46]:


plt.figure(figsize=(15,5))
plt.title('Продажи игр по жанрам 2011 - 2016гг', alpha=0.5, color="k", fontsize=18, fontstyle="italic", fontweight="bold", linespacing=10)
plt.grid()
ax = sns.barplot(y = 'med_sales', x = 'genre',  data=genre_pivot)


# Шутер - самый прибильный жанр, приключенческий и паззл отстающие, а остальные жанры можно сказать, идут ровно друг с другом 

# ## Шаг 4. Портрет пользователя каждого региона

# ### Самые популярные платформы (топ-5) пля пользователей каждого региона 

# Топ 5 платформ Северной Америки 

# In[47]:


na_sales = games_data_actual.pivot_table(index = 'platform', values = ['na_sales', 'total_sales'], aggfunc = 'sum')
na_sales.columns = ['na_sales', 'vs_total_sales']


# In[48]:


na_sales['vs_total_sales'] = na_sales['na_sales'] / na_sales['vs_total_sales']


# In[49]:


na_sales = na_sales.sort_values('na_sales').tail()


# In[50]:


display(na_sales)


# На северную Америку приходится более половины продаж игр на XOne и X360

# Топ 5 платформ Европы 

# In[51]:


eu_sales = games_data_actual.pivot_table(index = 'platform', values = ['eu_sales', 'total_sales'], aggfunc = 'sum')
eu_sales.columns = ['eu_sales', 'vs_total_sales']
eu_sales['vs_total_sales'] = eu_sales['eu_sales'] / eu_sales['vs_total_sales']
eu_sales = eu_sales.sort_values('eu_sales').tail()


# In[52]:


display(eu_sales)


# А в Европе в топе игры на ПК, больше половины продаж по миру 

# Топ 5 платформ Японии

# In[53]:


jp_sales = games_data_actual.pivot_table(index = 'platform', values = ['jp_sales', 'total_sales'], aggfunc = 'sum')
jp_sales.columns = ['jp_sales', 'vs_total_sales']
jp_sales['vs_total_sales'] = jp_sales['jp_sales'] / jp_sales['vs_total_sales']
jp_sales = jp_sales.sort_values('jp_sales').tail()


# In[54]:


display(jp_sales)


# Японцы верны отечественной PS. На PSP приходится более 80% мировых продаж

# PS4 и 3DS в топе во всех регионах

# ### Самые популярные жанры по регионам 

# Северная Америка

# In[55]:


na_genre = games_data_actual.pivot_table(index = 'genre', values = ['na_sales', 'total_sales'], aggfunc = 'sum')
na_genre.columns = ['na_sales', 'vs_total_sales']
na_genre['vs_total_sales'] = na_genre['na_sales'] / na_genre['vs_total_sales']
na_genre = na_genre.sort_values('na_sales').tail()


# In[56]:


display(na_genre)


# Европа

# In[57]:


eu_genre = games_data_actual.pivot_table(index = 'genre', values = ['eu_sales', 'total_sales'], aggfunc = 'sum')
eu_genre.columns = ['eu_sales', 'vs_total_sales']
eu_genre['vs_total_sales'] = eu_genre['eu_sales'] / eu_genre['vs_total_sales']
eu_genre = eu_genre.sort_values('eu_sales').tail()


# In[58]:


display(eu_genre)


# Япония 

# In[59]:


jp_genre = games_data_actual.pivot_table(index = 'genre', values = ['jp_sales', 'total_sales'], aggfunc = 'sum')
jp_genre.columns = ['jp_sales', 'vs_total_sales']
jp_genre['vs_total_sales'] = jp_genre['jp_sales'] / jp_genre['vs_total_sales']
jp_genre = jp_genre.sort_values('jp_sales').tail()


# In[60]:


display(jp_genre)


# Топ Европы и Америки схожи, когда в Японии распределение иное. Скорее всего дело в культуре. Япония как другой мир, соответственно, и увлечения у них другие. К тому же известно, что в Японии более популярны игры на телефонах, стоимость игр на консоли высока, поэтому они предпочитают покупать бу игры

# ### Влияние рейтинга  ESRB на продажи в отдельном регионе

# In[61]:


games_data_actual['rating'].unique()


# - M - для взрослых
# - E - для всех 
# - E10+ - старше 10 
# - T - для подростков 
# - EC - для детей младшего возраста 
# - RP - рейтинг ожидается 
# 
# nan учитывать не будем 
# 

# In[62]:


games_rating = games_data_actual.loc[games_data_actual['rating'] != 'nan'].pivot_table(index = 'rating', values = ['na_sales', 'eu_sales', 'jp_sales'], aggfunc = 'median')
games_rating.columns = ['na_sales', 'eu_sales', 'jp_sales']


# In[63]:


display(games_rating)


# In[64]:


plt.figure(figsize=(15,5))
plt.title('Влияние рейтинга ESRB на продажи в регионах', alpha=0.5, color="k", fontsize=18, fontstyle="italic", fontweight="bold", linespacing=10)
plt.xlabel('рейтинг')
plt.ylabel('продажи')
plt.grid()
plt.text(4, 0.4, "- M - для взрослых")
plt.text(4, 0.38, "- E - для всех")
plt.text(4, 0.35, "- E10+ - старше 10")
plt.text(4, 0.33, "- T - для подростков")
plt.text(4, 0.3, "- EC - для детей младшего возраста")
plt.text(4, 0.28, "- RP - рейтинг ожидается")
plt.plot(games_rating)
plt.legend(['Продажи в Японии', 'Продажи в Европе', 'Продажи в Америке'], bbox_to_anchor = (1, 0.6))
plt.show()


# Так как рейтинг американский, то правильно смотреть только на продажи в Америке
# 
# Лучше всего продаются игры для детей младшего возраста

# ## Шаг 5. Проверка гипотез
# 
# ### Средние пользовательские рейтинги платформ Xbox One и PC одинаковые

# - Нулевая гипотеза: Средний пользовательский рейтинг платформы XOne равен среднему пользовательскому рейтингу ПК
# 
# - Альтернативная гипотеза: Средний пользовательский рейтинг платформы XOne не равен среднему пользовательскому рейтингу ПК

# In[66]:


variance_xone = np.var(games_data_actual.loc[games_data_actual['platform'] == 'XOne']['user_score'])
print(variance_xone)


# In[67]:


variance_pc = np.var(games_data_actual.loc[games_data_actual['platform'] == 'PC']['user_score'])
print(variance_pc)


# Дисперсии отличаются, установим equal_var = False

# In[68]:


xone_score = games_data_actual.loc[(games_data_actual['platform'] == 'XOne') & (games_data_actual['user_score'] >= 0)]['user_score']
pc_score = games_data_actual.loc[(games_data_actual['platform'] == 'PC') & (games_data_actual['user_score'] >= 0)]['user_score']
alpha = .05
results = st.ttest_ind(xone_score, pc_score, equal_var = False)
print('p-значение: ', results.pvalue)

if (results.pvalue < alpha):
    print("Отвергаем нулевую гипотезу")
else:
    print("Не получилось отвергнуть нулевую гипотезу")
    
print('Средний пользовательский рейтинг XBox One', xone_score.mean())
print('Средний пользовательский рейтинг PC', pc_score.mean())


# Получается, средние пользовательские рейтинги платформ Xbox One и PC одинаковые. Скорее всего из-за того, что игры выходят сразу на нескольких платформах

# ### Средние пользовательские рейтинги жанров Action и Sports разные

# - Нулевая гипотеза: средний пользовательский рейтинг жанров экшн равен среднему пользовательскому рейтингу спортивных жанров
# - Альтернативная гипотеза: средний пользовательский рейтинг жанров экшн не равен среднему пользовательскому рейтингу спортивных жанров

# In[70]:


action_variance = np.var(games_data_actual.loc[games_data_actual['genre'] == 'Action']['user_score'])
print(action_variance)


# In[71]:


sports_variance = np.var(games_data_actual.loc[games_data_actual['genre'] == 'Sports']['user_score'])
print(sports_variance)


# Дисперсии отличаются, установим equal_var = False

# In[72]:


action_score = games_data_actual.loc[(games_data_actual['genre'] == 'Action') & (games_data_actual['user_score'] >= 0)]['user_score']
sports_score = games_data_actual.loc[(games_data_actual['genre'] == 'Sports') & (games_data_actual['user_score'] >= 0)]['user_score']
alpha = .05
results = st.ttest_ind(action_score, sports_score, equal_var = False)
print('p-значение: ', results.pvalue)
if (results.pvalue < alpha):
    print("Отвергаем нулевую гипотезу")
else:
    print("Не получилось отвергнуть нулевую гипотезу")
print('Средний пользовательский рейтинг жанра Action', action_score.mean())
print('Средний пользовательский рейтинг жанра Sports', sports_score.mean())


# Отвергаем нулевую гипотезу, значит, средние пользовательские рейтинги жанров Action и Sports разные. 

# ## Шаг 6. Общий вывод 

# Проведя исследования за актуальный период 2011-2016гг, мы выяснили:
# - Игры на разные платформы акуальны еще в течение 10 лет после выхода консоли. Первые 5 лет продажи растут, потом падают со скоростью роста
# - Последние консоли вышли в 2013 году, можно сделать упор на них
# - Продажи игр зависят от рейтингов критиков, оценки игроков чаще не влияют на покупаемость игры
# - Самый популярный жанр - шутер 
# - В США большей популярностью пользуется xBox, в Японии Xbox почти отсутствует, в Европе еще актуальны игры на ПК. Поэтому для планирования бюджета нужно учитывать рынок продаж
# - Игры для детей - самые продаваемые
# - Пользователи равно оценивают игры на различных платформах, а жанр влияет на оценку 
# 
