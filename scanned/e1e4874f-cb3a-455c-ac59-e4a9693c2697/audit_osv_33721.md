# [H] iTop admin can drop iTop database using webhooks

## Summary
Severity: High
Advisory: CVE-2025-49145
Aliases: GHSA-55q8-mfxr-pq4j
CVSS: 8.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:H)
Published: 2025-11-10
Source: https://osv.dev/vulnerability/CVE-2025-49145
Type: osv

## Details
Combodo iTop is a web based IT service management tool. In versions prior to 2.7.13 and 3.2.2, a user that has enough rights to create webhooks (mostly administrators) can drop the database. This is fixed in iTop 2.7.13 and 3.2.2 by verifying callback signature.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49145.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-55q8-mfxr-pq4j
- https://nvd.nist.gov/vuln/detail/CVE-2025-49145
