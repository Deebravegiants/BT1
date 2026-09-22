# [H] CVE-2026-28201

## Summary
Severity: High
Advisory: CVE-2026-28201
Aliases: GHSA-5wj9-f8q5-8f9c
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/CVE-2026-28201
Type: osv

## Details
An improper input validation, together with an overly permissive default CORS configuration in Open Notebook v1.8.1 allows remote attacker to trick a legitimate user to alter or delete arbitrary database entries via specially crafted malicious URL. Depending on the deployment, data exfiltration is also possible.

## References
- https://github.com/lfnovo/open-notebook/security/advisories/GHSA-5wj9-f8q5-8f9c
