from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        #Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            #Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")

## HTTP GET - Read Record## HTTP GET - Read Record

@app.route("/all")
def get_all_cafe():
    cafes=db.session.query(Cafe).all()

    return jsonify(cafe=[caf.to_dict() for caf in cafes],owner="rmrudro7@gmail.com")

@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    #Simply convert the random_cafe data record to a dictionary of key-value pairs.
    return jsonify(cafe=random_cafe.to_dict())
@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


# @app.route("/add", methods=["POST","GET"])
# def post_new_cafe():
#     new_cafe = Cafe(
#         name=request.form.get("name"),
#         map_url=request.form.get("map_url"),
#         img_url=request.form.get("img_url"),
#         location=request.form.get("loc"),
#         has_sockets=bool(request.form.get("sockets")),
#         has_toilet=bool(request.form.get("toilet")),
#         has_wifi=bool(request.form.get("wifi")),
#         can_take_calls=bool(request.form.get("calls")),
#         seats=request.form.get("seats"),
#         coffee_price=request.form.get("coffee_price"),
#     )
#
#     db.session.add(new_cafe)
#     db.session.commit()
#     return jsonify(cafe_details=new_cafe.to_dict(),response={"success": "Successfully added the new cafe."})





@app.route("/add", methods=["POST","GET"])
def post_new_cafe():
    # Check if all required fields are provided
    required_fields = ["name", "map_url", "img_url", "loc", "seats", "coffee_price"]
    for field in required_fields:
        if not request.form.get(field):
            return jsonify(response={"error": f"{field} is required."}), 400

    try:
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("loc"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )

        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(cafe_details=new_cafe.to_dict(), response={"success": "Successfully added the new cafe."})

    except IntegrityError as e:
        db.session.rollback()
        return jsonify(response={"error": "Database integrity error: " + str(e)}), 500





@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}) ,200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}) ,404



## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    print(api_key)
    if api_key == "TopSecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        print(cafe)

        if cafe:
            print(cafe.to_dict())
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(cafe_details=cafe.to_dict(),response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record




if __name__ == '__main__':
    app.run(debug=True)
