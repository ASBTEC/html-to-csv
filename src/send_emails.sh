
#!/usr/bin/env bash

# Usage
# Arg1: email value
# Arg2: relative path to qr file

email_value="$1"
file_name="$2"

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
    -F "file=@${PROJECT_FOLDER}/output/$file_name;type=text/html;encoder=base64" \
    -F '=)' \
    -H "Subject: Recepció del teu QR" \
    -H "From: Informatica ASBTEC <informatica@asbtec.cat>" \
    -H "To: ${EMAIL_USERNAME} <${EMAIL_USERNAME}>"
