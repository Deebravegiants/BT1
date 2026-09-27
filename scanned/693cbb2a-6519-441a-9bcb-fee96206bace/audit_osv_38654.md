# [C] FreeScout has Zip Slip path traversal in module installation that allows arbitrary file write leading to RCE

## Summary
Severity: Critical
Advisory: CVE-2026-41193
Aliases: GHSA-r85m-5mc9-cc9w
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-41193
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.215, FreeScout's module installation feature extracts ZIP archives without validating file paths, allowing an authenticated admin to write files arbitrarily on the server filesystem via a specially crafted ZIP. Version 1.8.215 fixes the vulnerability.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.215
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41193.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-r85m-5mc9-cc9w
- https://nvd.nist.gov/vuln/detail/CVE-2026-41193
- https://github.com/freescout-help-desk/freescout/commit/14f17a5cd22d217103a72b431b47b1f06996227b
