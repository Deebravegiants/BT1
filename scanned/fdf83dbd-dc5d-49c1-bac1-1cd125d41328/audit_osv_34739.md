# [H] Outline is vulnerable to privilege escalation vulnerability in document sharing

## Summary
Severity: High
Advisory: CVE-2025-64487
Aliases: GHSA-c8xf-3j86-7686
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2025-64487
Type: osv

## Details
Outline is a service that allows for collaborative documentation. Prior to 1.1.0, a privilege escalation vulnerability exists in the Outline document management system due to inconsistent authorization checks between user and group membership management endpoints. This vulnerability is fixed in 1.1.0.

## References
- https://github.com/outline/outline/releases/tag/v1.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64487.json
- https://github.com/outline/outline/security/advisories/GHSA-c8xf-3j86-7686
- https://nvd.nist.gov/vuln/detail/CVE-2025-64487
