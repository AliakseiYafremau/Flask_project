from flask import Flask, render_template, request, redirect
import sqlite3

"""Start of creating sql table"""
db = sqlite3.connect('sql_table.db')
cur = db.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS lessons(
    name text,
    grades text)
""")
db.commit()
db.close()
"""End of creating sql table"""


app = Flask(__name__)


@app.route('/')
def main():
    """downloading of main page"""
    database = sqlite3.connect('sql_table.db')
    cursor = database.cursor()
    cursor.execute("SELECT name FROM lessons")
    name_list = cursor.fetchall()
    database.close()
    return render_template('main_page.html', list_of_names_of_lesson=name_list)


@app.route('/', methods=['POST'])
def getting_new_lesson():
    new_lesson = request.form['new_lesson']
    database = sqlite3.connect('sql_table.db')
    cursor = database.cursor()
    tuple_new_lesson = (new_lesson, '')
    cursor.execute("INSERT INTO lessons VALUES (?, ?)", tuple_new_lesson)
    database.commit()
    database.close()
    return main()


@app.route('/<lsn>')
def lesson(lsn):
    database = sqlite3.connect('sql_table.db')
    cursor = database.cursor()
    cursor.execute("SELECT * FROM lessons")
    lesson_list = cursor.fetchall()
    for el in lesson_list:
        if el[0] == lsn:
            string_of_grades = el[1]
            break
        else:
            string_of_grades = ''
    if string_of_grades != '':
        grade_list = string_of_grades.split(' ')
        av = 0
        for i in grade_list:
            av += float(i)
        av /= len(grade_list)
    else:
        grade_list = []
        av = 'Enter number'
    database.close()
    return render_template('lesson_page.html', lesson=lsn, list_of_grades=grade_list, average=av)


@app.route('/<lsn>', methods=['POST'])
def getting_new_grade(lsn):
    new_grade = request.form['new_grade']
    if new_grade.isnumeric():
        database = sqlite3.connect('sql_table.db')
        cursor = database.cursor()
        cursor.execute("SELECT * FROM lessons")
        name_list = cursor.fetchall()
        for el in name_list:
            if el[0] == lsn:
                use_grades = el[1]
                break
        if use_grades != '':
            updated_grades = '{} {}'.format(use_grades, new_grade)
        else:
            updated_grades = '{}'.format(new_grade)
        cursor.execute("UPDATE lessons SET grades = '{}' WHERE name= '{}' ".format(updated_grades, lsn))
        database.commit()
        database.close()
    return lesson(lsn)


@app.route('/<lsn>/deleted')
def delete(lsn):
    database = sqlite3.connect('sql_table.db')
    cursor = database.cursor()
    param = (lsn,)
    cursor.execute("DELETE FROM lessons WHERE name= (?) ", param)
    database.commit()
    database.close()
    return redirect('/')


@app.route('/<lsn>/<deleted_grade>')
def delete_grade(lsn, deleted_grade):
    database = sqlite3.connect('sql_table.db')
    cursor = database.cursor()
    cursor.execute("SELECT * FROM lessons")
    name_list = cursor.fetchall()
    for el in name_list:
        if el[0] == lsn:
            use_grades = el[1]
            break
    if use_grades == '': # если оценок нет
        pass
    elif ' ' not in use_grades: # если оценка одна
        if deleted_grade == use_grades:
            cursor.execute("UPDATE lessons SET grades = '' WHERE name = '{}' ".format(lsn))
    elif deleted_grade == use_grades[:use_grades.find(' ')]:
        use_grades = use_grades[use_grades.find(' ')+1:]
        cursor.execute("UPDATE lessons SET grades = '{}' WHERE name= '{}' ".format(use_grades, lsn))
    elif deleted_grade == use_grades[:use_grades.find(' ')]:
        use_grades = use_grades[:use_grades.find(' ') + 1]
        cursor.execute("UPDATE lessons SET grades = '{}' WHERE name= '{}' ".format(use_grades, lsn))
    else: # если оценка в центре
        if deleted_grade in use_grades:
            index = use_grades.index(deleted_grade)
            use_grades = use_grades[:index-1] + use_grades[index+1:]
            cursor.execute("UPDATE lessons SET grades = '{}' WHERE name= '{}' ".format(use_grades, lsn))
    database.commit()
    database.close()
    return redirect('/{}'.format(lsn))


app.run(debug=True)
