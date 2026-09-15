# [H] SuiteCRM is Vulnerable to Authenticated Time Based Blind SQL Injection

## Summary
Severity: High
Advisory: CVE-2025-64492
Aliases: GHSA-54m4-4p54-j8hp
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-08
Source: https://osv.dev/vulnerability/CVE-2025-64492
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. Versions 8.9.0 and below contain a time-based blind SQL Injection vulnerability. This vulnerability allows an authenticated attacker to infer data from the database by measuring response times, potentially leading to the extraction of sensitive information. It is possible for an attacker to enumerate database, table, and column names, extract sensitive data, or escalate privileges. This is fixed in version 8.9.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64492.json
- https://github.com/SuiteCRM/SuiteCRM-Core/security/advisories/GHSA-54m4-4p54-j8hp
- https://nvd.nist.gov/vuln/detail/CVE-2025-64492
