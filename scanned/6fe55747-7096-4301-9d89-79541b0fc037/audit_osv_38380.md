# [H] BoidCMS: Local File Inclusion (LFI) leads to Remote Code Execution (RCE) via tpl parameter

## Summary
Severity: High
Advisory: CVE-2026-39387
Aliases: GHSA-45xp-xw54-6cv6
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-39387
Type: osv

## Details
BoidCMS is an open-source, PHP-based flat-file CMS for building simple websites and blogs, using JSON as its database. Versions prior to 2.1.3 are vulnerable to a critical Local File Inclusion (LFI) attack via the tpl parameter, which can lead to Remote Code Execution (RCE).The application fails to sanitize the tpl (template) parameter during page creation and updates. This parameter is passed directly to a require_once() statement without path validation. An authenticated administrator can exploit this by injecting path traversal sequences (../) into the tpl value to escape the intended theme directory and include arbitrary files — specifically, files from the server's media/ directory. When combined with the file upload functionality, this becomes a full RCE chain: an attacker can first upload a file with embedded PHP code (e.g., disguised as image data), then use the path traversal vulnerability to include that file via require_once(), executing the embedded code with web server privileges. This issue has been fixed in version 2.1.3.

## References
- https://github.com/BoidCMS/BoidCMS/releases/tag/v2.1.3
- https://github.com/BoidCMS/BoidCMS/security/advisories/GHSA-45xp-xw54-6cv6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39387.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-39387
