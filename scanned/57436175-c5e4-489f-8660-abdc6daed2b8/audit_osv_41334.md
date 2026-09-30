# [C] CVE-2026-59561

## Summary
Severity: Critical
Advisory: CVE-2026-59561
Aliases: GHSA-6x2x-729r-wjh5
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-59561
Type: osv

## Details
Sakura Editor provided by Sakura Editor Development Community contains an OS command injection vulnerability. If a victim user is directed to edit a file in a crafted directory, arbitrary OS command may be executed on the user's PC when the user invokes "Open Terminal".

## References
- https://github.com/sakura-editor/sakura/releases/tag/v2.4.3
- https://jvn.jp/en/jp/JVN74538868/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59561.json
- https://github.com/sakura-editor/sakura/security/advisories/GHSA-6x2x-729r-wjh5
- https://nvd.nist.gov/vuln/detail/CVE-2026-59561
