from flask_restful import Resource, reqparse
from app.db import get_db


class ProductsAPI(Resource):
    """
    产品列表 (Products)
    """

    def get(self):
        '''
        获取所有产品
        ---
        tags:
          - Products
        description: 检索所有产品信息
        responses:
          200:
            description: 返回产品列表
        '''
        connection = get_db()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM products;")
        rows = cursor.fetchall()
        cursor.close()

        products = [
            {"id": row[0], "name": row[1], "inventory": row[2], "price": float(row[3])}
            for row in rows
        ]

        return {"products": products}, 200

    def post(self):
        '''
        添加一个新产品
        ---
        tags:
          - Products
        description: 添加一个新产品到库存
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                  description: 产品名称
                inventory:
                  type: integer
                  description: 库存数量
                price:
                  type: number
                  description: 产品价格
        responses:
          201:
            description: 产品成功添加
        '''
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, type=str, help="产品名称必需")
        parser.add_argument('inventory', required=True, type=int, help="库存数量必需")
        parser.add_argument('price', required=True, type=float, help="价格必需")
        args = parser.parse_args()

        connection = get_db()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO products (name, inventory, price) VALUES (%s, %s, %s);",
            (args['name'], args['inventory'], args['price'])
        )
        connection.commit()
        cursor.close()

        return {"message": "产品成功添加"}, 201


class ProductAPI(Resource):
    """
    单个产品 (Product)
    """

    def get(self, product_id):
        '''
        获取单个产品
        ---
        tags:
          - Products
        description: 根据产品 ID 获取单个产品
        parameters:
          - name: product_id
            in: path
            required: true
            type: integer
            description: 产品 ID
        responses:
          200:
            description: 返回单个产品信息
          404:
            description: 产品未找到
        '''
        connection = get_db()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM products WHERE id = %s;", (product_id,))
        row = cursor.fetchone()
        cursor.close()

        if row:
            return {
                "product": {
                    "id": row[0],
                    "name": row[1],
                    "inventory": row[2],
                    "price": float(row[3])
                }
            }, 200
        else:
            return {"message": "找不到产品"}, 404

    def put(self, product_id):
        '''
        更新单个产品
        ---
        tags:
          - Products
        description: 更新单个产品信息
        parameters:
          - name: product_id
            in: path
            required: true
            type: integer
            description: 产品 ID
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                  description: 产品名称
                inventory:
                  type: integer
                  description: 库存数量
                price:
                  type: number
                  description: 产品价格
        responses:
          200:
            description: 产品成功更新
          404:
            description: 产品未找到
        '''
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=False, type=str)
        parser.add_argument('inventory', required=False, type=int)
        parser.add_argument('price', required=False, type=float)
        args = parser.parse_args()

        connection = get_db()
        cursor = connection.cursor()

        # 检查产品是否存在
        cursor.execute("SELECT * FROM products WHERE id = %s;", (product_id,))
        if not cursor.fetchone():
            cursor.close()
            return {"message": "找不到产品"}, 404

        # 动态更新字段
        updates = []
        values = []
        for key, value in args.items():
            if value is not None:
                updates.append(f"{key} = %s")
                values.append(value)
        values.append(product_id)

        update_query = f"UPDATE products SET {', '.join(updates)} WHERE id = %s;"
        cursor.execute(update_query, tuple(values))
        connection.commit()
        cursor.close()

        return {"message": "产品成功更新"}, 200

    def delete(self, product_id):
        '''
        删除单个产品
        ---
        tags:
          - Products
        description: 根据产品 ID 删除单个产品
        parameters:
          - name: product_id
            in: path
            required: true
            type: integer
            description: 产品 ID
        responses:
          200:
            description: 产品成功删除
          404:
            description: 产品未找到
        '''
        connection = get_db()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s;", (product_id,))
        connection.commit()
        cursor.close()

        return {"message": "产品成功删除"}, 200


class ProductsQueryAPI(Resource):
    """
    产品条件查询 (Products Query)
    """

    def get(self):
        '''
        条件查询产品
        ---
        tags:
          - Products
        description: 根据条件查询产品
        parameters:
          - name: name
            in: query
            type: string
            required: false
            description: 产品名称 (模糊查询)
          - name: inventory
            in: query
            type: integer
            required: false
            description: 库存数量
          - name: price_min
            in: query
            type: float
            required: false
            description: 最低价格
          - name: price_max
            in: query
            type: float
            required: false
            description: 最高价格
        responses:
          200:
            description: 返回符合条件的产品列表
          404:
            description: 找不到符合条件的产品
        '''
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='args')
        parser.add_argument('inventory', type=int, location='args')
        parser.add_argument('price_min', type=float, location='args')
        parser.add_argument('price_max', type=float, location='args')
        args = parser.parse_args()

        query = "SELECT * FROM products WHERE 1=1"  # 初始化基础查询
        values = []

        if args['name']:
            query += " AND name LIKE %s"
            values.append(f"%{args['name']}%")  # 模糊查询

        if args['inventory']:
            query += " AND inventory = %s"
            values.append(args['inventory'])  # 精确匹配库存

        if args['price_min']:
            query += " AND price >= %s"
            values.append(args['price_min'])  # 最低价格

        if args['price_max']:
            query += " AND price <= %s"
            values.append(args['price_max'])  # 最高价格

        connection = get_db()
        cursor = connection.cursor()
        cursor.execute(query, tuple(values))
        rows = cursor.fetchall()
        cursor.close()

        if rows:
            products = [
                {
                    "id": row[0],
                    "name": row[1],
                    "inventory": row[2],
                    "price": float(row[3])
                }
                for row in rows
            ]
            return {"products": products}, 200
        else:
            return {"message": "找不到产品"}, 404
