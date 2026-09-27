# [H] Xibo: Authenticated Server-Side Request Forgery (SSRF) in Library Upload via URL functionality

## Summary
Severity: High
Advisory: CVE-2026-42141
Aliases: GHSA-fwq8-c4gw-pxmh
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-42141
Type: osv

## Details
Xibo is an open source digital signage platform with a web content management system and Windows display player software. Prior to 4.4.1, an authenticated Server-Side Request Forgery (SSRF) vulnerability in the Xibo CMS allows users with Library upload permissions to make arbitrary HTTP requests from the CMS server to internal or external network resources. This can be exploited to scan internal infrastructure, access local cloud metadata endpoints (e.g., AWS IMDS), interact with internal services that lack authentication, or exfiltrate data. This vulnerability is fixed in 4.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42141.json
- https://github.com/xibosignage/xibo-cms/security/advisories/GHSA-fwq8-c4gw-pxmh
- https://nvd.nist.gov/vuln/detail/CVE-2026-42141
