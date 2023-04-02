import pandas as pd
from tkinter import *
import random
import datetime
import os

# 读取Excel文件
df = pd.read_excel('words.xls', header=None)

# 获取单词列表和意思列表
words = df[0].tolist()
phonetics = df[1].tolist()
meanings = df[2].tolist()

# 初始化当前单词位置和是否认识
current_word_idx = 0
known_words = []
unknown_words = []

# 定义记忆曲线的时间间隔（天）
memory_curve = [1, 2, 4, 7, 15, 30, 90, 180]

# 尝试读取已有的记忆曲线文件
# 尝试读取已有的记忆曲线文件
if os.path.exists('memory_curve.xlsx'):
    memory_df = pd.read_excel('memory_curve.xlsx')
    memory_dict = memory_df.set_index('Word').to_dict()['Level']
else:
    memory_df = pd.DataFrame(columns=['Word', 'Level', 'Date'])
    memory_dict = {}

# 随机选择一个单词
def generate_word():
    global current_word_idx
    idx = random.randint(0, len(words) - 1)
    word = words[idx]
    # 检查单词是否在记忆曲线中，如果是，判断是否需要复习
    if word in memory_dict:
        level = memory_dict[word]
        if level < len(memory_curve):
            # 获取单词上次学习的日期
            last_date = datetime.datetime.strptime(memory_df.loc[memory_df['Word'] == word, 'Date'].values[0], '%Y-%m-%d')
            # 获取今天的日期
            today_date = datetime.datetime.now()
            # 计算两个日期之间的天数差
            delta_days = (today_date - last_date).days
            # 如果天数差小于记忆曲线的时间间隔，跳过这个单词
            if delta_days < memory_curve[level]:
                return generate_word()
    # 如果单词不在记忆曲线中，或者需要复习，返回这个单词的信息
    current_word_idx = idx
    return words[idx], phonetics[idx], meanings[idx]

# 开始新词汇的学习
def start_learning():
    known_button.grid(row=1, column=0, pady=20)
    unknown_button.grid(row=1, column=1, pady=20)
    show_word()


# 显示单词
def show_word():
    word, phonetic, meaning = generate_word()
    canvas.itemconfig(word_text, text=word)
    canvas.itemconfig(phonetic_text, text="")
    canvas.itemconfig(meaning_text, text="")
    known_button.grid(row=1, column=0, pady=20)
    unknown_button.grid(row=1, column=1, pady=20)


# 认识这个单词
def known_word():
    # 获取当前单词
    word = words[current_word_idx]
    # 把当前单词的等级设为0
    memory_dict[word] = 0
    # 把当前单词的索引添加到known_words列表中
    known_words.append(current_word_idx)
    word_phonetic = phonetics[current_word_idx]
    word_meaning = meanings[current_word_idx]
    canvas.itemconfig(phonetic_text, text=word_phonetic)
    canvas.itemconfig(meaning_text, text=word_meaning)
    known_button.grid_forget()
    unknown_button.grid_forget()
    next_button.grid(row=1, column=0, pady=20)
    wrong_button.grid(row=1, column=1, pady=20)


# 不认识这个单词
def unknown_word():
    unknown_words.append(current_word_idx)
    word_phonetic = phonetics[current_word_idx]
    word_meaning = meanings[current_word_idx]
    canvas.itemconfig(meaning_text, text=word_meaning)
    known_button.grid_forget()
    unknown_button.grid_forget()
    next_button.grid(row=2, column=0, pady=20, columnspan=2)
    wrong_button.grid_forget()
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)


# 记错了这个单词
def wrong_word():
    unknown_words.append(current_word_idx)
    next_word()


# 显示下一个单词
def next_word():
    word_phonetic = phonetics[current_word_idx]
    word_meaning = meanings[current_word_idx]
    canvas.itemconfig(phonetic_text, text=word_phonetic)
    canvas.itemconfig(meaning_text, text=word_meaning)
    next_button.grid_forget()
    wrong_button.grid_forget()
    show_word()


# 创建GUI界面
window = Tk()
window.title("艾宾浩斯记忆曲线单词学习")
window.config(padx=50, pady=50, bg="#ffffff")

# 创建Canvas
canvas = Canvas(width=400, height=300, bg="#ffffff", highlightthickness=0)
canvas.grid(row=0, column=0, columnspan=2)

# 添加单词、音标和意思文本
word_text = canvas.create_text(200,
                               100,
                               text="",
                               font=("Arial", 36, "bold"),
                               fill="#3c3c3c")
phonetic_text = canvas.create_text(200,
                                   150,
                                   text="",
                                   font=("Arial", 18),
                                   fill="#8c8c8c")
meaning_text = canvas.create_text(200,
                                  220,
                                  text="",
                                  font=("Arial", 18),
                                  fill="#3c3c3c",
                                  width=280)

# 添加"认识"和"不认识"按钮
known_button = Button(text="认识",
                      font=("Arial", 14, "bold"),
                      bg="#f2c94c",
                      activebackground="#f2b63c",
                      borderwidth=0,
                      command=known_word)
unknown_button = Button(text="不认识",
                        font=("Arial", 14, "bold"),
                        bg="#f2994a",
                        activebackground="#f2853c",
                        borderwidth=0,
                        command=unknown_word)

# 添加"下一个"和"记错了"按钮
next_button = Button(text="下一个",
                     font=("Arial", 14, "bold"),
                     bg="#f2c94c",
                     activebackground="#f2b63c",
                     borderwidth=0,
                     command=next_word)
wrong_button = Button(text="记错了",
                      font=("Arial", 14, "bold"),
                      bg="#f2994a",
                      activebackground="#f2853c",
                      borderwidth=0,
                      command=wrong_word)

# 开始新词汇的学习
start_learning()

# 运行GUI
window.mainloop()

# 将认识的单词和不认识的单词保存到Excel中
know_df = pd.DataFrame({
    'Word': [words[i] for i in known_words],
    'Level': [memory_dict.get(words[i], -1) + 1 for i in known_words],
    'Date': [datetime.datetime.now().strftime('%Y-%m-%d')] * len(known_words)
})
unknown_df = pd.DataFrame({
    'Word': [words[i] for i in unknown_words],
    'Level': [0] * len(unknown_words),
    'Date': [datetime.datetime.now().strftime('%Y-%m-%d')] * len(unknown_words)
})
# 合并已有的数据和新的数据
new_df = pd.concat([memory_df, know_df, unknown_df], ignore_index=True)
# 去除重复的单词，只保留最新的记录
new_df = new_df.drop_duplicates(subset=['Word'], keep='last')
# 重新排序索引
new_df = new_df.reset_index(drop=True)
# 保存到Excel中
with pd.ExcelWriter('memory_curve.xlsx') as writer:
    new_df.to_excel(writer, sheet_name='Memory', index=False, header=True)
