
#!/usr/bin/env bash

# Usage
# Arg1: email value


email_value="$1"

my_file_path=
for file_path in output/*; do
  my_file_path=$file_path
done

print_args()
{
  echo "from: $EMAIL_USERNAME"
  echo "to: $email_value"
  echo "pass: **"
}

PROJECT_FOLDER="$(cd "$(dirname "$(realpath "$0")")/../" &>/dev/null && pwd)"

curl -v --url 'smtps://smtp.gmail.com:465' \
  --ssl-reqd \
  --mail-from "${EMAIL_USERNAME}" \
  --mail-rcpt "${email_value}" \
  --mail-rcpt "${EMAIL_USERNAME}" \
  --mail-rcpt "informatica@asbtec.cat" \
  --user "${EMAIL_USERNAME}:${EMAIL_PASSWORD}" \
  -F '=(;type=multipart/mixed' \
  -F "=Hola

Aquí tens el fitxer CSV que has sol·licitat amb formulari a la vocalia d'informàtica.

Aquest missatge ha estat generat automàticament. Per a qualsevol dubte o incidència, pots contactar-nos a informatica@asbtec.cat.

Fins aviat!

Atentament,

A


;type=text/plain" \
    -F "file=@${PROJECT_FOLDER}/$my_file_path;type=text/html;encoder=base64" \
    -F '=)' \
    -H "Subject: Recepció del teu QR" \
    -H "From: Informatica ASBTEC <informatica@asbtec.cat>" \
    -H "To: ${EMAIL_USERNAME} <${EMAIL_USERNAME}>"
