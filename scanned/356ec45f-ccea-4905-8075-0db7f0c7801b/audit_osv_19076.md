# [H] CVE-2020-7013

## Summary
Severity: High
Advisory: CVE-2020-7013
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-03
Source: https://osv.dev/vulnerability/CVE-2020-7013
Type: osv

## Details
Kibana versions before 6.8.9 and 7.7.0 contain a prototype pollution flaw in TSVB. An authenticated attacker with privileges to create TSVB visualizations could insert data that would cause Kibana to execute arbitrary code. This could possibly lead to an attacker executing code with the permissions of the Kibana process on the host system.

## References
- https://www.elastic.co/community/security/
