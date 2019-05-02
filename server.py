#!/system/bin/env python3

from flask import Flask, request, redirect, url_for, render_template
import html
import calendar
import db_utils
import response

app = Flask(__name__)


@app.route('/')
@app.route('/category/<int:categoryId>')
def getIndex(categoryId=0):
    categories = db_utils.getCategories()
    items = db_utils.getItems(categoryId)
    for item in items:
        item.nice_date = '{month} {day}, {year}'.format(month=calendar.month_name[item.created_at.month], day=item.created_at.day, year=item.created_at.year)
    return render_template('index.html', categories=categories, items=items)


@app.route('/category/new', methods=['GET', 'POST'])
@app.route('/category/<int:id>/edit', methods=['GET', 'POST'])
def getEditCategoryPage(id=0):
    if request.method == 'GET':
        if id and id != 0:
            # id is specified, render edit category page
            category=db_utils.getCategory(id)
            return render_template('edit-category.html', category=category)
        else:
            return render_template('edit-category.html')
    elif request.method == 'POST':
        if request.form['name'] and request.form['desc']:
            if id and id != 0:
                # id is specified, update existing category
                category=db_utils.updateCategory(
                    id, request.form['name'], request.form['desc'])
                categoryData={'id': category.id,
                    'name': category.name, 'desc': category.desc}
                return response.success(url_for('getIndex'), categoryData)
            else:
                category=db_utils.addCategory(
                    request.form['name'], request.form['desc'])
                categoryData={'id': category.id,
                    'name': category.name, 'desc': category.desc}
                return response.success(url_for('getIndex'), categoryData)


@app.route('/delete/category/<int:id>', methods=['POST'])
def postDeleteCategory(id):
    db_utils.deleteCategory(id)
    return response.success()



@app.route('/item/new', methods=['GET', 'POST'])
@app.route('/item/<int:id>/edit', methods=['GET', 'POST'])
def getEditItemPage(id=0):
    if request.method == 'GET':
        if id and id != 0:
            # id is specified, render edit item page
            item=db_utils.getItem(id)
            categories=db_utils.getCategories()
            return render_template('edit-item.html', item=item, categories=categories)
        else:
            # id is not specified, render new item page
            categories=db_utils.getCategories()
            return render_template('edit-item.html', categories=categories)
    elif request.method == 'POST':
        if id and id != 0:
            if request.form['name'] and request.form['desc'] and request.form['cat-id']:
                item=db_utils.updateItem(
                    request.form['item-id'], request.form['name'], request.form['desc'], request.form['cat-id'])
                itemData={'id': item.id, 'name': item.name, 'desc': item.desc,
                    'short_desc': item.short_desc, 'category_id': item.category_id}
                return response.success(url_for('getItemPage', id=itemData['id']), itemData)
            else:
                return "ERROR"
        else:
            if request.form['name'] and request.form['desc'] and request.form['cat-id']:
                item=db_utils.addItem(
                    request.form['name'], request.form['desc'], request.form['cat-id'])
                itemData={'id': item.id, 'name': item.name, 'desc': item.desc,
                    'short_desc': item.short_desc, 'category_id': item.category_id}
                return response.success(url_for('getItemPage', id=itemData['id']), itemData)
            else:
                return "ERROR"

@app.route('/item/<int:id>', methods=['GET'])
def getItemPage(id):
    categories=db_utils.getCategories()
    item=db_utils.getItem(id)
    return render_template('item.html', id=id, categories=categories, item=item)


@app.route('/delete/item/<int:id>', methods=['POST'])
def postDeleteItem(id):
    item=db_utils.getItem(id)
    db_utils.deleteItem(item)
    return response.success()


if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0', port=8000, threaded=False)
