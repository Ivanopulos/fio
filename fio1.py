import pandas as pd

df_meetingbase = pd.read_excel('combined_data_with_votes.xlsx', dtype=str)
df_gender = pd.read_excel('gndr.xlsx', dtype=str)
# Создаем столбец с вторым словом из "ФИО правообладателя"
df_meetingbase['second_name'] = df_meetingbase['ФИО правообладателя'].apply(
    lambda x: x.split()[1] if isinstance(x, str) and len(x.split()) > 1 else None
)
# Объединяем df_meetingbase и df_gender
df_meetingbase = df_meetingbase.merge(df_gender, left_on='second_name', right_on='name', how='left')
# Переименовываем столбец gender из df_gender для ясности
df_meetingbase.rename(columns={'gender': 'gender_matched'}, inplace=True)
# Удаляем временный столбец second_name, если он больше не нужен
df_meetingbase.drop('second_name', axis=1, inplace=True)

print(df_meetingbase)
