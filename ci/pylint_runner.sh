#!/bin/bash

# run pylint
pylint $(ls -d */) --load-plugins=pylint_django --disable="C0111,R1705,E0401" | tee pylint.txt

# get badge
mkdir public
score=$(sed -n 's/^Your code has been rated at \([-0-9.]*\)\/.*/\1/p' pylint.txt)
anybadge --value=$score --file=public/pylint.svg pylint
echo "Pylint score was $score"

# get html
pylint --load-plugins=pylint_json2html $(ls -d */) --disable="C0111,R1705" --output-format=jsonextended > pylint.json
pylint-json2html -f jsonextended -o public/pylint.html pylint.json

#cleanup
rm pylint.txt pylint.json

exit 0

