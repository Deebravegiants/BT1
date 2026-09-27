# [M] Frappe Learning vulnerable to Malicious Content upload via Profile bio field

## Summary
Severity: Medium
Advisory: CVE-2025-59415
Aliases: GHSA-h7gh-3vq5-96jx
CVSS: 4.6 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2025-59415
Type: osv

## Details
Frappe Learning is a learning system that helps users structure their content. In versions 2.34.1 and below, there is a security vulnerability in Frappe Learning where the system did not adequately sanitize the content uploaded in the profile bio. Malicious SVG files could be used to execute arbitrary scripts in the context of other users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59415.json
- https://github.com/frappe/lms/security/advisories/GHSA-h7gh-3vq5-96jx
- https://nvd.nist.gov/vuln/detail/CVE-2025-59415
- https://github.com/frappe/lms/commit/ed162e254690772365d4d1365f176b59bc4db72d
