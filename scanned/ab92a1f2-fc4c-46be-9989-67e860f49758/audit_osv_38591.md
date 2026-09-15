# [H] mailcow: dockerized vulnerable to Second Order SQL Injection in quarantine category via API

## Summary
Severity: High
Advisory: CVE-2026-40871
Aliases: GHSA-r8fq-wrfm-cj2q
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40871
Type: osv

## Details
mailcow: dockerized is an open source groupware/email suite based on docker. Versions prior to 2026-03b have a second-order SQL injection vulnerability in the quarantine_category field via the Mailcow API. The /api/v1/add/mailbox endpoint stores quarantine_category without validation or sanitization. This value is later used by quarantine_notify.py, which constructs SQL queries using unsafe % string formatting instead of parameterized queries. This results in a delayed (second-order) SQL injection when the quarantine notification job executes, allowing an attacker to inject arbitrary SQL. Using a UNION SELECT, sensitive data (e.g., admin credentials) can be exfiltrated and rendered inside quarantine notification emails. Version 2026-03b fixes the vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40871.json
- https://github.com/mailcow/mailcow-dockerized/security/advisories/GHSA-r8fq-wrfm-cj2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-40871
