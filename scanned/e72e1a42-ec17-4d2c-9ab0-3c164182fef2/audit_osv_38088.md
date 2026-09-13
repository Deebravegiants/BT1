# [M] Postiz: SSRF in upload-from-url endpoint allows fetching internal resources and cloud metadata

## Summary
Severity: Medium
Advisory: CVE-2026-34576
Aliases: GHSA-89vp-m2qw-7v34
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34576
Type: osv

## Details
Postiz is an AI social media scheduling tool. Prior to version 2.21.3, the POST /public/v1/upload-from-url endpoint accepts a user-supplied URL and fetches it server-side using axios.get() with no SSRF protections. The only validation is a file extension check (.png, .jpg, etc.) which is trivially bypassed by appending an image extension to any URL path. An authenticated API user can fetch internal network resources, cloud instance metadata, and other internal services, with the response data uploaded to storage and returned to the attacker. This issue has been patched in version 2.21.3.

## References
- https://github.com/gitroomhq/postiz-app/releases/tag/v2.21.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34576.json
- https://github.com/gitroomhq/postiz-app/security/advisories/GHSA-89vp-m2qw-7v34
- https://nvd.nist.gov/vuln/detail/CVE-2026-34576
