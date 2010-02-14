"""
No description.
"""

S.open('/sahana')
S.clickAndWait('link=Register')
S.click('t2_person_name')
S.storeRandom('8', 'user')
S.storeRandom('8', 'domain')
S.store('${user}@${domain}.com', 'email')
S.type('t2_person_name', '${user}')
S.type('t2_person_email', '${email}')
S.storeRandom('8', 'password')
S.type('t2_person_password', '${password}')
S.clickAndWait('//input[@value=\'Submit\']')
S.verifyTextPresent('You have been successfully registered')
S.open('/sahana/default/login')
S.clickAndWait('link=Logout')
S.verifyTextPresent('Logged Out')
S.open('/sahana/default/login')
S.clickAndWait('link=Login')
S.type('t2_person_email', '${email}')
S.type('t2_person_password', '${password}')
S.clickAndWait('//input[@value=\'Submit\']')
S.verifyTextPresent('Logged In')
