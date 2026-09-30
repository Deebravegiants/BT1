# [H] Initiative Allows Unauthenticated Access to Uploaded Documents via Public /uploads/ Endpoint

## Summary
Severity: High
Advisory: CVE-2026-28276
Aliases: GHSA-w34j-fx72-h2pq
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-28276
Type: osv

## Details
Initiative is a self-hosted project management platform. An access control vulnerability exists in Initiative versions prior to 0.32.2 where uploaded documents are served from a publicly accessible /uploads/ directory without any authentication or authorization checks. Any uploaded file can be accessed directly via its URL by unauthenticated users (e.g., in an incognito browser session), leading to potential disclosure of sensitive documents. The problem was patched in v0.32.2, and the patch was further improved on in 032.4.

## References
- https://github.com/Morelitea/initiative/releases/tag/v0.32.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28276.json
- https://github.com/Morelitea/initiative/security/advisories/GHSA-w34j-fx72-h2pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-28276
