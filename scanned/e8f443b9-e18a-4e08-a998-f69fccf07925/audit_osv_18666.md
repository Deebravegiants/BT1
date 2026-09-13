# [C] CVE-2020-35131

## Summary
Severity: Critical
Advisory: CVE-2020-35131
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-08
Source: https://osv.dev/vulnerability/CVE-2020-35131
Type: osv

## Details
Cockpit before 0.6.1 allows an attacker to inject custom PHP code and achieve Remote Command Execution via registerCriteriaFunction in lib/MongoLite/Database.php, as demonstrated by values in JSON data to the /auth/check or /auth/requestreset URI.

## References
- https://github.com/agentejo/cockpit/commits/next/lib/MongoLite/Database.php
- https://github.com/agentejo/cockpit/releases/tag/0.6.1
- https://www.exploit-db.com/exploits/49390
