# [C] OpenBullet2 0.3.2 Authenticated RCE via FileProxySource Script Upload

## Summary
Severity: Critical
Advisory: CVE-2026-25855
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-25855
Type: osv

## Details
OpenBullet2 through version 0.3.2 contains a remote code execution vulnerability that allows authenticated users to execute arbitrary commands by uploading script files (.bat.ps1.sh) through the FileProxySource proxy loading feature. Attackers can upload malicious script files as proxy sources, causing the server to execute the scripts and return output as proxy lines, resulting in arbitrary command execution on the host as the process user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25855.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25855
- https://www.vulncheck.com/advisories/openbullet2-authenticated-rce-via-fileproxysource-script-upload
- https://github.com/openbullet/openbullet2
- https://hackernoon.com/one-empty-header-to-admin-how-an-auth-bypass-breaks-openbullet2
