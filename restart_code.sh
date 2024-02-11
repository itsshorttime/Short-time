echo "------------create migration---------------"
set FLASK_APP=main
echo "------------migration----------------------"
set FLASK_ENV=development
echo "------------restart server------------------"
flask --app main run