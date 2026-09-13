# [H] CVE-2020-7012

## Summary
Severity: High
Advisory: CVE-2020-7012
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-03
Source: https://osv.dev/vulnerability/CVE-2020-7012
Type: osv

## Details
Kibana versions 6.7.0 to 6.8.8 and 7.0.0 to 7.6.2 contain a prototype pollution flaw in the Upgrade Assistant. An authenticated attacker with privileges to write to the Kibana index could insert data that would cause Kibana to execute arbitrary code. This could possibly lead to an attacker executing code with the permissions of the Kibana process on the host system.

## References
- https://www.elastic.co/community/security/
