# cookbook/schema.py
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from ingredients.models import Category, Ingredient

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "ingredients")

class IngredientType(DjangoObjectType):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "notes", "category")



class CategoryNode(DjangoObjectType):
    class Meta:
        model = Category
        filter_fields = ['name', 'ingredients']
        interfaces = (graphene.relay.Node, )


class IngredientNode(DjangoObjectType):
    class Meta:
        model = Ingredient
        # Allow for some more advanced filtering here
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'notes': ['exact', 'icontains'],
            'category': ['exact'],
            'category__name': ['exact'],
        }
        interfaces = (graphene.relay.Node, )


class IngredientsQuery(graphene.ObjectType):
    ingredients__ = graphene.List(IngredientType)
    category_by_name = graphene.Field(CategoryType, name=graphene.String(required=True))

    category = graphene.relay.Node.Field(CategoryNode)
    all_categories = DjangoFilterConnectionField(CategoryNode)

    ingredient = graphene.relay.Node.Field(IngredientNode)
    all_ingredients = DjangoFilterConnectionField(IngredientNode)



    def resolve_all_ingredients(root, info):
        return Ingredient.objects.all()

    def resolve_category_by_name(root, info, name):
        try:
            return Category.objects.get(name=name)
        except Category.DoesNotExist:
            return None


# mutations create  
class CategoryInput(graphene.InputObjectType):
	name = graphene.String()


class IngredientInput(graphene.InputObjectType):
	category = graphene.List(graphene.ID)
	name = graphene.String()
	notes = graphene.String()
     

class CreateCategory(graphene.Mutation):
	class Arguments:
		input = CategoryInput(required=True)

	category = graphene.Field(CategoryType)
	ok = graphene.Boolean(default_value=False)

	@staticmethod
	def mutate(parent, info, input=None):
		category_instance = Category.objects.create(name=input.name)
		ok = True
		return CreateCategory(category=category_instance, ok=ok)

class UpdateCategory(graphene.Mutation):
	class Arguments:
		id = graphene.Int(required=True)
		input = CategoryInput()

	category = graphene.Field(CategoryType)
	ok = graphene.Boolean(default_value=False)

	@staticmethod
	def mutate(parent, info, id, input=None):
		category_instance = Category.objects.get(id=id)
		category_instance.name = input.name if input.name is not None else category_instance.name
		category_instance.save()
		ok = True
		return UpdateCategory(category=category_instance, ok=ok)

class DeleteCategory(graphene.Mutation):
	class Arguments:
		id = graphene.ID()

	category = graphene.Field(CategoryType)
	ok = graphene.Boolean(default_value=False)

	@staticmethod
	def mutate(parent, info, id):
		category_instance = Category.objects.get(id=id)
		category_instance.delete()
		ok = True
		return DeleteCategory(category=category_instance, ok=ok)

class CreateIngredient(graphene.Mutation):
  class Arguments:
    input = IngredientInput()

  ingredient = graphene.Field(IngredientType)
  ok = graphene.Boolean(default_value=False)

  @staticmethod
  def mutate(parent, info, input=None):
    print(input.category)
    category = Category.objects.get(id=input.category[0])
    ingredient_instance = Ingredient.objects.create(name=input.name,notes=input.notes,category_id=category.id)
    ok = True
    return CreateIngredient(ingredient=ingredient_instance, ok=ok)

class Mutation(graphene.ObjectType):
	create_category = CreateCategory.Field()
	update_category = UpdateCategory.Field()
	delete_category = DeleteCategory.Field()
	create_ingredient = CreateIngredient.Field()



"""
mutation createCategory {
createCategory(input: {name: "hassan"}) {
category {
    id
    name
    }
    ok
}
}
#####
mutation updateCategory {
  updateCategory(id: 3, input: {name: "ffdfd"}) {
    category {
      id
      name
    }
    ok
  }
}
or
mutation one(everything can write here){
  updateCategory(id: 3, input: {name: "ffdfd"}) {
    category {
      id
      name
    }
    ok
  }
}
#####
mutation deleteCategory {
  deleteCategory(id: 2) {
    category {
      name
    }
    ok
  }
}
#######
mutation createIngredient {
  createIngredient(input: {category: [1], name: "hassan", notes: "bbbbb"}) {
    ingredient {
      id
      name
      notes
      category {
        id
        name
      }
    }
    ok
  }
}
"""