# [C] DataEase H2 RCE via Zip Protocol & File Dropper Fix bypass

## Summary
Severity: Critical
Advisory: CVE-2026-55633
Aliases: GHSA-8x36-774q-pwqg
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-55633
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to 2.10.24, a bypass of the H2 zip protocol and file dropper fix allows an authenticated attacker to upload a zip archive disguised with a .ttf extension through FontManage.saveFile and then exploit it through the zip protocol to achieve remote code execution. This issue is fixed in version 2.10.24.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55633.json
- https://github.com/dataease/dataease/security/advisories/GHSA-8x36-774q-pwqg
- https://nvd.nist.gov/vuln/detail/CVE-2026-55633
- https://github.com/dataease/dataease/commit/265b31179f1427c059f739841f2e39aaa6d1b937
- https://github.com/dataease/dataease/commit/8892a6945b0b7a329a156155270fae58afa895bc
