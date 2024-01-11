import pandas as pd

df_meetingbase = pd.read_excel('combined_data_with_votes.xlsx', dtype=str)
df_gender = pd.read_excel('gndr.xlsx', dtype=str)
def extract_word(name, index):
    if isinstance(name, str) and len(name.split()) > index:
        return name.split()[index]
    return None
df_meetingbase['second_name'] = df_meetingbase['ФИО правообладателя'].apply(lambda x: extract_word(x, 1))# Извлекаем второе слово
df_meetingbase = df_meetingbase.merge(df_gender, left_on='second_name', right_on='name', how='left', suffixes=('', '_y'))# Объединяем df_meetingbase и df_gender по второму слову
mask = df_meetingbase['gender'].isnull() & df_meetingbase['ФИО правообладателя'].apply(lambda x: isinstance(x, str) and len(x.split()) == 4)# Для записей, где gender не найден и есть четыре слова в ФИО, пытаемся найти по третьему слову
df_meetingbase.loc[mask, 'third_name'] = df_meetingbase['ФИО правообладателя'].apply(lambda x: extract_word(x, 2))
merged_df = df_meetingbase[mask].merge(df_gender, left_on='third_name', right_on='name', how='left', suffixes=('', '_y'))
df_meetingbase.loc[mask, 'gender'] = merged_df['gender_y']
df_meetingbase.drop(['second_name', 'third_name'], axis=1, inplace=True)# Убираем временные столбцы
def gender_from_lastname(name):
    if name.endswith('на'):
        return 'f'
    elif name.endswith('ич'):
        return 'm'
    return None
df_meetingbase['gender'] = df_meetingbase.apply(
    lambda row: gender_from_lastname(row['ФИО правообладателя']) if row['gender'] not in ['f', 'm'] else row['gender'],
    axis=1
)
def gender_from_firstname(name):
    if name.endswith('ов'):
        return 'm'
    elif name.endswith('ва'):
        return 'f'
    return None
df_meetingbase.loc[df_meetingbase['gender'].isin(['m', 'f']) == False, 'gender'] = df_meetingbase[df_meetingbase['gender'].isin(['m', 'f']) == False]['ФИО правообладателя'].apply(lambda x: x.split()[0] if isinstance(x, str) else None).apply(gender_from_firstname)
df_meetingbase.loc[df_meetingbase['gender'].isnull(), 'gender'] = 'u'

def modify_name_based_on_gender(name, gender):
    if not isinstance(name, str):
        return name

    words = name.split()
    if gender == 'f':
        # Для женского пола: изменяем окончания слов
        if words[0].endswith('ая'):
            words[0] = words[0][:-2] + 'ую'
        else:
            words = [w[:-1] + 'ю' if w.endswith('я') and words.index(w) in [1, 2] else w for w in words]
        words = [w[:-1] + 'у' if w.endswith('а') else w for w in words]

    elif gender == 'm':
        # Для мужского пола: изменяем окончания слов
        if words[0].endswith('в'):
            words[0] = words[0][:-1] + 'ва'
        if words[0].endswith('ий') or words[0].endswith('ый'):
            words[0] = words[0][:-2] + 'ого'
        if words[0][-1] in 'бвгджзклмнпрстфхцчшщ':
            words[0] = words[0] + 'а'
        if len(words) > 1 and words[1][-1] in 'бвгджзклмнпрстфхцчшщ':
            words[1] = words[1] + 'а'
        if len(words) > 1 and words[1].endswith('авела'):
            words[1] = words[1][:-5] + 'авла'
        if words[1].endswith('й') or words[1].endswith('ь'):
            words[1] = words[1][:-1] + 'я'
        elif words[1].endswith('я'):
            words[1] = words[1][:-1] + 'ю'
        if words[-1].endswith('ич'):
            words[-1] = words[-1] + 'а'

    return ' '.join(words)

df_meetingbase['кого'] = df_meetingbase.apply(                     # Создаем столбец "кого" с изменениями
    lambda row: modify_name_based_on_gender(row['ФИО правообладателя'], row['gender']), axis=1)
df_meetingbase.to_excel('1.xlsx', index=False)

