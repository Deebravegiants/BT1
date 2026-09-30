# [M] SolidInvoice's long-lived API tokens accepted as URL query parameters, exposing credentials in server logs and browser history

## Summary
Severity: Medium
Advisory: CVE-2026-61614
Aliases: GHSA-mp4c-675j-mv67
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-61614
Type: osv

## Details
SolidInvoice is an open-source invoicing platform. Prior to version 3.0.1, the REST API authenticator accepts bearer tokens via a `?token=` URL query parameter as a fallback to the `X-API-TOKEN` header. This causes long-lived API credentials to be recorded in server access logs, proxy logs, browser history, and HTTP Referer headers sent to third-party origins. Version 3.0.1 fixes the issue.

## References
- https://github.com/SolidInvoice/SolidInvoice/releases/tag/3.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61614.json
- https://github.com/SolidInvoice/SolidInvoice/security/advisories/GHSA-mp4c-675j-mv67
- https://nvd.nist.gov/vuln/detail/CVE-2026-61614
