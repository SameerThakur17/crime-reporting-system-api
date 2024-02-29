from marshmallow import Schema, fields


class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class ComplaintSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    location = fields.Str(required=True)
    date = fields.Date(required=True)
    status = fields.Str(dump_only=True)
    user_id = fields.Int(dump_only=True)


class UserSchema(PlainUserSchema):
    complaints = fields.List(fields.Nested(ComplaintSchema(), dump_only=True))


class ComplaintUpdateSchema(Schema):
    title = fields.Str()
    description = fields.Str()
    location = fields.Str()
    date = fields.Date()
