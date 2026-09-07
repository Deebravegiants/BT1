# [M] NocoDB: Stored Cross-Site Scripting via Secure Attachment

## Summary
Severity: Medium
Advisory: GHSA-6mhr-74x2-98v9
CVE: CVE-2026-53929
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-6mhr-74x2-98v9
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0

## Details
### Summary
With `NC_SECURE_ATTACHMENTS=true`, an authenticated uploader could deliver `.html` or
`.svg` attachments that the browser rendered inline from the NocoDB origin instead of
forcing a download.

### Details
The signed attachment handler stored response-header overrides under PascalCase keys
(`ResponseContentDisposition`, `ResponseContentType`) while the controller that served
the file read them under lowercase-hyphen names (`response-content-disposition`). The
mismatch dropped the `Content-Disposition: attachment` header, leaving Express to
auto-render `.html`, `.svg`, and similar inline. The fix corrects the key case and
additionally forces `Content-Disposition: attachment` and
`Content-Type: application/octet-stream` for any MIME type not on the preview
allowlist.

### Impact
Stored Cross-Site Scripting in the NocoDB origin from inline-rendered uploads. Script
executing in the victim's browser can read the auth JWT from `localStorage`.
Exploitation requires authenticated upload permission and the secure-attachment mode
to be enabled.

### Credit
This issue was reported by [@bugbunny-research](https://github.com/bugbunny-research).
It was independently reported by [@DavidCarliez](https://github.com/DavidCarliez).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-6mhr-74x2-98v9
- https://nvd.nist.gov/vuln/detail/CVE-2026-53929
- https://github.com/nocodb/nocodb
