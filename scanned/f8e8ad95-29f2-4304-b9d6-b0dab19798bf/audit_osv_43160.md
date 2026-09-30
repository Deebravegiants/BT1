# [H] Idurar IDURAR ERP CRM - Broken Access Control

## Summary
Severity: High
Advisory: CVE-2026-72600
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72600
Type: osv

## Details
A broken access control vulnerability in Idurar IDURAR ERP CRM 4.1.0 allows unauthenticated remote attackers to download invoice PDF files containing customer PII via the /download router. The router is mounted without authentication middleware, making it publicly accessible. An attacker can enumerate MongoDB ObjectIds to download any invoice in the system without credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72600.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72600
- https://github.com/idurar/idurar-erp-crm
