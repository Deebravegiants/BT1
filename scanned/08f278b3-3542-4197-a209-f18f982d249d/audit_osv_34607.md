# [M] ClipBucket path traversal vulnerability in template editor allows arbitrary file read and write

## Summary
Severity: Medium
Advisory: CVE-2025-62424
Aliases: GHSA-3v2p-rfwx-52qj
CVSS: 6.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/CVE-2025-62424
Type: osv

## Details
ClipBucket is a web-based video-sharing platform. In ClipBucket version 5.5.2 - #146 and earlier, the /admin_area/template_editor.php endpoint is vulnerable to path traversal. The validation of the file-loading path is inadequate, allowing authenticated administrators to read and write arbitrary files outside the intended template directory by inserting path traversal sequences into the folder parameter. An attacker with administrator privileges can exploit this vulnerability to read sensitive files such as /etc/passwd and modify writable files on the system, potentially leading to sensitive information disclosure and compromise of the application or server. This issue is fixed in version 5.5.2 - #147.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62424.json
- https://github.com/MacWarrior/clipbucket-v5/security/advisories/GHSA-3v2p-rfwx-52qj
- https://nvd.nist.gov/vuln/detail/CVE-2025-62424
- https://github.com/MacWarrior/clipbucket-v5/commit/c06d0f2e69c9acb008cebbd34fd5f29da3191a28
