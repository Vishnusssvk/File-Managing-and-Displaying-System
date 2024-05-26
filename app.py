from datetime import datetime
from flask import Flask, render_template, redirect, request,jsonify,Response
from flask_cors import CORS
import mimetypes
import base64
import io
import pymongo
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import DateField, StringField
from bson import ObjectId
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key' 
uri = "mongodb+srv://username:password@cluster0.lexpcdj.mongodb.net/mydatabase?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(uri)
db = client['project']
mydb = db['managingdata']
class UploadForm(FlaskForm):
    image = FileField('Image', validators=[FileRequired()])
    document = FileField('Document', validators=[FileRequired()])
    description = StringField('Description')
    startdate_field = DateField('Start Date', format='%Y-%m-%d')
    enddate_field = DateField('End Date', format='%Y-%m-%d')

@app.route('/display')
def display():
    documents = mydb.find({'$or': [{'image': {'$exists': True}}, {'document': {'$exists': True}}]})
    imagelist = []
    for document in documents:
        id=document.get('_id')
        description = document.get('description', 'No description available')
        startdate=document.get('Start date','-')
        enddate=document.get('End date','-')
        imagelist.append({
            "_id":id,
            'description': description,
            'Start date':startdate,
            'End date':enddate,
            'image': document.get('image'),
            'document': document.get('document')
        })
    return render_template('display.html', imagelist=imagelist)
@app.route('/',methods=['POST', 'GET'])
def upload():
    form = UploadForm()
    if request.method == 'POST':
      if form.validate_on_submit():
         if form.validate_on_submit():
            image = form.image.data
            file = form.document.data
            description = form.description.data
            start_date=form.startdate_field.data
            end_date=form.enddate_field.data
         if image.filename == '':
            print('empty')
            return redirect(request.url)

         if file.filename == '':
            mydb.insert_one({'document': 'NO FILE TO DISPLAY','image': encoded_data, 'description': description})
            return render_template('project.html',form=form)
         else:
              image_data = image.read()
              description = request.form['description']
              encoded_data = base64.b64encode(image_data).decode()
              file_data = file.read()
              encoded_data1 = base64.b64encode(file_data).decode()
              start_date = datetime(start_date.year, start_date.month, start_date.day)
              end_date = datetime(end_date.year, end_date.month, end_date.day)
              mydb.insert_one({'document': encoded_data1, 'description': description,'image': encoded_data,'Start date':start_date,'End date':end_date})

         return 'Document and image upload successful.'
    return render_template('project.html',form=form)
@app.route('/delete_document/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    try:
        result = mydb.delete_one({'_id': ObjectId(document_id)})
        print(document_id)
        if result.deleted_count == 1:
            return jsonify({'message': 'Document deleted successfully.'}), 200
        else:
            return jsonify({'message': 'Document not found or already deleted.'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@app.route('/download/<document_id>')
def download_document(document_id):
    try:
        document_data = mydb.find_one({'_id': ObjectId(document_id)})
        if not document_data:
            return jsonify({'message': 'Document not found.'}), 404
        
        document_bytes = base64.b64decode(document_data['document'])
        
        file_extension = mimetypes.guess_extension(mimetypes.guess_type(document_data.get('filename', 'unknown.pdf'))[0])
        if file_extension == '.pdf':
            mimetype = 'application/pdf'
        else:
            return jsonify({'message': 'Unsupported file type.'}), 400
        return Response(io.BytesIO(document_bytes), mimetype=mimetype, headers={'Content-Disposition': 'attachment; filename=document{}'.format(file_extension)})
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000,debug=True)

