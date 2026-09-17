# [M] Remote Code Execution (RCE) vulnerability in super-xray via URL input

## Summary
Severity: Medium
Advisory: CVE-2022-41945
Aliases: GHSA-732j-763p-cvqg
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-11-21
Source: https://osv.dev/vulnerability/CVE-2022-41945
Type: osv

## Details
super-xray is a vulnerability scanner (xray) GUI launcher. In version 0.1-beta, the URL is not filtered and directly spliced ​​into the command, resulting in a possible RCE vulnerability. Users should upgrade to super-xray 0.2-beta.

## References
- https://github.com/4ra1n/super-xray/releases/tag/0.2-beta
- https://github.com/4ra1n/super-xray/security/advisories/GHSA-732j-763p-cvqg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41945.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41945
