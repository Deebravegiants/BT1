# [M] GLPI is Vulnerable to SSRF via Webhooks

## Summary
Severity: Medium
Advisory: CVE-2026-22247
Aliases: GHSA-f6f6-v3qr-9p5x
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-22247
Type: osv

## Details
GLPI is a free asset and IT management software package. From version 11.0.0 to before 11.0.5, a GLPI administrator can perform SSRF request through the Webhook feature. This issue has been patched in version 11.0.5.

## References
- https://github.com/glpi-project/glpi/releases/tag/11.0.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22247.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-f6f6-v3qr-9p5x
- https://nvd.nist.gov/vuln/detail/CVE-2026-22247
