#!/usr/bin/env bash
set -euo pipefail

email_value="$1"

# pick the (only) file from output/
my_file_path=
for file_path in output/*; do
  my_file_path="$file_path"
done

PROJECT_FOLDER="$(cd "$(dirname "$(realpath "$0")")/../" &>/dev/null && pwd)"
ATTACH_PATH="${PROJECT_FOLDER}/${my_file_path}"
ATTACH_NAME="$(basename "$ATTACH_PATH")"

# RFC 2047-encoded UTF-8 subject (Recepció del teu QR)
SUBJECT_ENC="=?UTF-8?B?UmVjZXBjacOzIGRlbCB0ZXUgQ1NW?="

curl -v --url 'smtps://smtp.gmail.com:465' \
  --ssl-reqd \
  --mail-from "${EMAIL_USERNAME}" \
  --mail-rcpt "${email_value}" \
  --user "${EMAIL_USERNAME}:${EMAIL_PASSWORD}" \
  -F '=(;type=multipart/mixed' \
  -F "=Hola\n\nAquí tens el fitxer CSV que has sol·licitat amb formulari a la vocalia d\'informàtica.\n\nAquest missatge ha estat generat automàticament. Per a qualsevol dubte o incidència, pots contactar-nos a informatica@asbtec.cat.\n\nFins aviat!\n\nAtentament,\n\nASBTEC\n;type=text/plain" \
  -F "file=@${ATTACH_PATH};type=text/csv;charset=utf-8;encoder=base64;filename=${ATTACH_NAME}" \
  -F '=)' \
  -H "MIME-Version: 1.0" \
  -H "Subject: ${SUBJECT_ENC}" \
  -H 'From: "Informàtica ASBTEC" <informatica@asbtec.cat>' \
  -H "To: <${email_value}>"
