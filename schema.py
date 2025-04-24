import graphene
import accounts.schema
from ingredients import schema
import accounts

class Query(schema.IngredientsQuery, accounts.schema.AccountsQuery,graphene.ObjectType):
    pass


class Mutation(schema.Mutation, accounts.schema.Mutation, graphene.ObjectType):
	pass

schema = graphene.Schema(query=Query,mutation=Mutation)