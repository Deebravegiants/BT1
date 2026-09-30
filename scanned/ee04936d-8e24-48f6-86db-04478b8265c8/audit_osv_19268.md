# [C] CVE-2020-9433

## Summary
Severity: Critical
Advisory: CVE-2020-9433
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-02-27
Source: https://osv.dev/vulnerability/CVE-2020-9433
Type: osv

## Details
openssl_x509_check_email in lua-openssl 0.7.7-1 mishandles X.509 certificate validation because it uses lua_pushboolean for certain non-boolean return values.

## References
- https://github.com/zhaozg/lua-openssl/commit/a6dc186dd4b6b9e329a93cca3e7e3cfccfdf3cca
