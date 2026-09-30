# [H] CVE-2019-10049

## Summary
Severity: High
Advisory: CVE-2019-10049
CVSS: 7.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2019-05-31
Source: https://osv.dev/vulnerability/CVE-2019-10049
Type: osv

## Details
It is possible for an attacker with regular user access to the web application of Pydio through 8.2.2 to trick an administrator user into opening a link shared through the application, that in turn opens a shared file that contains JavaScript code (that is executed in the context of the victim user to obtain sensitive information such as session identifiers and perform actions on behalf of him/her).

## References
- https://www.secureauth.com/labs/advisories
