# [C] SiYuan: Lute HTML sanitizer allows `<iframe>` tags in Bazaar package README, leading to arbitrary command execution via SiYuan Electron client

## Summary
Severity: Critical
Advisory: CVE-2026-54759
Aliases: GHSA-r6v5-4c66-f6pw
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-54759
Type: osv

## Details
SiYuan is an open-source personal knowledge management system. Prior to 3.7.0, Lute's HTML sanitizer does not remove <iframe> elements. Combined with the SiYuan Electron client's permissive security configuration, an attacker can include a malicious <iframe> in a Bazaar package README that executes arbitrary commands on the victim's machine when the package details are viewed. No package installation is required. This vulnerability is fixed in 3.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54759.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-r6v5-4c66-f6pw
- https://nvd.nist.gov/vuln/detail/CVE-2026-54759
