# [H] CVE-2019-20138

## Summary
Severity: High
Advisory: CVE-2019-20138
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-12-30
Source: https://osv.dev/vulnerability/CVE-2019-20138
Type: osv

## Details
The HTTP Authentication library before 2019-12-27 for Nim has weak password hashing because the default algorithm for libsodium's crypto_pwhash_str is not used.

## References
- https://github.com/FedericoCeratto/nim-httpauth/commit/15fd0686dc363075c08976ad897d6c92e1e6283c
