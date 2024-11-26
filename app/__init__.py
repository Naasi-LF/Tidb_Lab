from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from app.resources import ProductsAPI, ProductAPI, ProductsQueryAPI

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # 初始化 Swagger
    swagger_config = {
        "swagger": "2.0",
        "info": {
            "title": "库存管理 API",
            "description": "库存管理系统的 API 文档",
            "version": "1.0.0",
        },
    }
    Swagger(app, template=swagger_config)

    # 初始化 RESTful API
    api = Api(app)
    api.add_resource(ProductsAPI, '/api/products')  # 注册获取所有产品的接口
    api.add_resource(ProductAPI, '/api/products/<int:product_id>')  # 注册获取单个产品的接口
    api.add_resource(ProductsQueryAPI, '/api/products/query') # 注册资源
    
    return app

