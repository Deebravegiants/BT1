# [M] LocalAI - Server-Side Request Forgery via POST /models/apply

## Summary
Severity: Medium
Advisory: CVE-2026-59707
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-59707
Type: osv

## Details
LocalAI contains an unauthenticated server-side request forgery vulnerability in the POST /models/apply endpoint that allows attackers to fetch arbitrary internal URLs. The endpoint passes unsanitized gallery URL fields directly to gallery.GetGalleryConfigFromURLWithContext without proper validation, enabling attackers to force the server to issue HTTP GET requests to private and loopback ranges with partial response content leaked through error messages.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59707.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59707
- https://www.vulncheck.com/advisories/localai-server-side-request-forgery-via-post-models-apply
- https://github.com/mudler/LocalAI/issues/10665
- https://github.com/mudler/LocalAI/commit/f9b968e19d7cbc556d59dceb2e0e450b828a3fda
- https://github.com/mudler/LocalAI
