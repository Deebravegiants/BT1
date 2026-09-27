# [H] CVE-2017-10140

## Summary
Severity: High
Advisory: CVE-2017-10140
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-16
Source: https://osv.dev/vulnerability/CVE-2017-10140
Type: osv

## Details
Postfix before 2.11.10, 3.0.x before 3.0.10, 3.1.x before 3.1.6, and 3.2.x before 3.2.2 might allow local users to gain privileges by leveraging undocumented functionality in Berkeley DB 2.x and later, related to reading settings from DB_CONFIG in the current directory.

## References
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://www.postfix.org/announcements/postfix-3.2.2.html
- https://access.redhat.com/errata/RHSA-2019:0366
- http://seclists.org/oss-sec/2017/q3/285
