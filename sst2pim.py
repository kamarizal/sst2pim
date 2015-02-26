import urllib2
import cookielib
import urllib
import re
import sys
import time

def chkacctexist(acctname):
    search_dict = {
        'AccountName': acctname, 
        'PageNo': '1', 
        'NoRecordsPerPage': '10', 
        'X-Requested-With': 'XMLHttpRequest'
    }
    search_data = urllib.urlencode(search_dict)
    search = opener.open('https://pim/PV/AccountGet', search_data, timeout=20)
    content = search.read()
    if re.search(r'Login', content):
        print "Unable to check",name
    pattern = search_dict['AccountName']
    match = re.compile(pattern)

    if match.search(content):
        return "yes"


def splitpassword(passwd):
    chunk = []
    length = len(passwd)
    if length % 2 == 0:
        offset = length/2
        chunk.append(passwd[0:offset])
        chunk.append(passwd[offset:length]) 
    else:
        leneven = length - 1
        offset = leneven/2
        chunk.append(passwd[0:offset])
        chunk.append(passwd[offset:length])

    return chunk
 

# Login
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

 # login credential
login_data = urllib.urlencode(
    {
        'username': 'user', 
        'password': 'password',
        'domain': '.com.my'
    }
)
try:
    login = opener.open('https://pim/Account/Login?ReturnUrl=/',
        login_data, timeout=20)
    responselogin = login.read()
    if re.search(r'Welcome', responselogin):
        print "Login OK"
    else:
        print "Error in Login"
        sys.exit()
except urllib2.HTTPError as e:
    print e.code, e.reason



# Open file and add to custodian
file = open('file.txt', 'r')
count = 1
for line in file:
    name, username, passwd, address = line.split(';')
    passsplit = splitpassword(passwd)
    add_dict = {
        "Id": "-1", 
        "Name": name, 
        "Username": username, 
        "FirstPassword": passsplit[0], 
        "SecondPassword": passsplit[1], 
        "FirstPasswordConfirm": passsplit[0], 
        "SecondPasswordConfirm": passsplit[1], 
        "IsSplitPassword": "false", 
        "FirstHalfGroupId": "", 
        "SecondHalfGroupId": "", 
        "Address": address, 
        "Port": "0", 
        "AccessMethod": "", 
        "IsUseGateway": "false", 
        "GatewayId": "", 
        "Oper": "add", 
        "X-Requested-With": "XMLHttpRequest"
    }
    
    if chkacctexist(name):
        print name,"already exist. Skip"
        continue
    else:
        add_data = urllib.urlencode(add_dict)
        try:
            response = opener.open('https://pim/PV/AccountEdit',
                add_data, timeout=20)

            # Not login. Exit
            if re.search(r'Login', response.geturl()):
                print "Not Login. Unable to add",name,"Exit"
                sys.exit()
            else:
                print count,"Add",name
                time.sleep( 1 )

        except urllib2.HTTPError as e:
            print e.code, e.reason
            sys.exit()

        # get new added account id
        getid_dict = {
            'AccountName': name, # custodian acct name
            'PageNo': '1', 
            'NoRecordsPerPage': '10', 
            'X-Requested-With': 'XMLHttpRequest'
        }
        getid_data = urllib.urlencode(getid_dict)
        get_idresponse = opener.open('https://pim/PV/AccountGet',
            getid_data, timeout=20)
        html_idresponse = get_idresponse.read()
        matchid = re.compile(
            '<tr class="content-row idvalue" recordid="(?P<record_id>\d+)">',
            re.IGNORECASE | re.MULTILINE
        )
        getid = matchid.search(html_idresponse)
        rcdid = getid.group('record_id')

        #  add to SST safe
        safe_dict = { 
            'Id': '16', # the is of the safe
            'AccountIds': rcdid, 
            'X-Requested-With': 'XMLHttpRequest'
        }
        safe_dict_encoded = urllib.urlencode(safe_dict)
        opener.open('https://pim/PV/AccountAssignmentAdd', safe_dict_encoded,
            timeout=20)
        print "Add",name,"to SST safe"
        time.sleep( 1 )
        count += 1

#Logout
opener.open('https://pim/Account/Logout')
print "Done"