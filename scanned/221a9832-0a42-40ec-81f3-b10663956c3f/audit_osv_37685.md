# [M] Hytale Modding Wiki has Insecure Direct Object Reference / GDPR PII Exposure

## Summary
Severity: Medium
Advisory: CVE-2026-32736
Aliases: GHSA-xvq7-wwhx-x2fh
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-32736
Type: osv

## Details
The Hytale Modding Wiki is a free service for Hytale mods to host their documentation & wikis. An Insecure Direct Object Reference (IDOR) vulnerability in versions of the wiki prior to 1.0.0 exposes mod authors' personal information - including full names and email addresses - to any authenticated user who visits a mod page. Any user who creates an account can access sensitive author details by simply navigating to a mod's page via its slug. Version 1.0.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32736.json
- https://github.com/HytaleModding/wiki/security/advisories/GHSA-xvq7-wwhx-x2fh
- https://nvd.nist.gov/vuln/detail/CVE-2026-32736
- https://github.com/HytaleModding/wiki/commit/4a96b3f9bce9a9d34030c39a8d6e4c6b6183f13d
