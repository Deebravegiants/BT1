# [H] Sylde has Improper Control of Generation of Code

## Summary
Severity: High
Advisory: CVE-2026-26974
Aliases: GHSA-w7h5-55jg-cq2f
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-26974
Type: osv

## Details
Slyde is a program that creates animated presentations from XML. In versions 0.0.4 and below, Node.js automatically imports **/*.plugin.{js,mjs} files including those from node_modules, so any malicious package with a .plugin.js file can execute arbitrary code when installed or required. All projects using this loading behavior are affected, especially those installing untrusted packages. This issue has been fixed in version 0.0.5. To workaround this issue, users can audit and restrict which packages are installed in node_modules.

## References
- https://github.com/Tygo-van-den-Hurk/Slyde/releases/tag/v0.0.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26974.json
- https://github.com/Tygo-van-den-Hurk/Slyde/security/advisories/GHSA-w7h5-55jg-cq2f
- https://nvd.nist.gov/vuln/detail/CVE-2026-26974
- https://github.com/Tygo-van-den-Hurk/Slyde/commit/e4c215b061e44fd2ead805de34d72642a710af60
