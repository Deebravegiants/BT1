# [H] Server-Side Request Forgery Vulnerability in Computer Vision Annotation Tool (CVAT)

## Summary
Severity: High
Advisory: CVE-2022-31188
Aliases: GHSA-7vpj-j5xv-29pr
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2022-08-01
Source: https://osv.dev/vulnerability/CVE-2022-31188
Type: osv

## Details
CVAT is an opensource interactive video and image annotation tool for computer vision. Versions prior to 2.0.0 were found to be subject to a Server-side request forgery (SSRF) vulnerability. Validation has been added to urls used in the affected code path in version 2.0.0. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- http://packetstormsecurity.com/files/169814/CVAT-2.0-Server-Side-Request-Forgery.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31188.json
- https://github.com/cvat-ai/cvat/security/advisories/GHSA-7vpj-j5xv-29pr
- https://nvd.nist.gov/vuln/detail/CVE-2022-31188
- https://github.com/cvat-ai/cvat/commit/6fad1764efd922d99dbcda28c4ee72d071aa5a07
