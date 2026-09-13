# [H] SolidInvoice: PHP unserialize() called on client-controlled data in DataGrid LiveComponent context prop

## Summary
Severity: High
Advisory: CVE-2026-61686
Aliases: GHSA-4gj8-frx2-gmp6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-61686
Type: osv

## Details
SolidInvoice is an open-source invoicing platform. Prior to version 3.0.1, the `DataGrid` LiveComponent deserializes a `context` prop value using PHP's `unserialize()` after receiving it from the client. Because the prop is marked `writable: true`, an authenticated attacker can supply an arbitrary PHP serialized payload. Version 3.0.1 fixes the issue.

## References
- https://github.com/SolidInvoice/SolidInvoice/releases/tag/3.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61686.json
- https://github.com/SolidInvoice/SolidInvoice/security/advisories/GHSA-4gj8-frx2-gmp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-61686
