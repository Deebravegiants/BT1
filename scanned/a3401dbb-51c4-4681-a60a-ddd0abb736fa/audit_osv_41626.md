# [C] Vvveb CMS 1.0.8.2 Remote Code Execution via Media Upload

## Summary
Severity: Critical
Advisory: CVE-2026-6249
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-6249
Type: osv

## Details
Vvveb CMS 1.0.8.2 contains a remote code execution vulnerability in its media upload handler that allows authenticated attackers to execute arbitrary operating system commands by uploading a PHP webshell with a .phtml extension. Attackers can bypass the extension deny-list and upload malicious files to the publicly accessible media directory, then request the file over HTTP to achieve full server compromise.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6249.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6249
- https://www.vulncheck.com/advisories/vvveb-cms-remote-code-execution-via-media-upload
- https://github.com/givanz/Vvveb/commit/23ac0e8c758d80f3c4d9224763c8b2359648270e
