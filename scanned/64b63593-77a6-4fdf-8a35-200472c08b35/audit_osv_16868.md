# [M] CVE-2020-10104

## Summary
Severity: Medium
Advisory: CVE-2020-10104
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-03-05
Source: https://osv.dev/vulnerability/CVE-2020-10104
Type: osv

## Details
An issue was discovered in Zammad 3.0 through 3.2. After authentication, it transmits sensitive information to the user that may be compromised and used by an attacker to gain unauthorized access. Hashed passwords are returned to the user when visiting a certain URL.

## References
- https://zammad.com/news/security-advisory-zaa-2020-04
