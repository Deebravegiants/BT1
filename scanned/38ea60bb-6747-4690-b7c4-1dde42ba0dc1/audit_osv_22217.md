# [C] Code injection in iTunesRPC-Remastered

## Summary
Severity: Critical
Advisory: CVE-2022-23603
Aliases: GHSA-3xpp-rhqx-cw96
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:L)
Published: 2022-02-01
Source: https://osv.dev/vulnerability/CVE-2022-23603
Type: osv

## Details
iTunesRPC-Remastered is a discord rich presence application for use with iTunes & Apple Music. In code before commit 24f43aa user input is not properly sanitized and code injection is possible. Users are advised to upgrade as soon as is possible. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23603.json
- https://github.com/bildsben/iTunesRPC-Remastered/security/advisories/GHSA-3xpp-rhqx-cw96
- https://nvd.nist.gov/vuln/detail/CVE-2022-23603
- https://github.com/bildsben/iTunesRPC-Remastered/commit/24f43aac0f4116b3d89fdbe973ba92c6cfb0d998
- https://github.com/bildsben/iTunesRPC-Remastered/commit/54b02d9f3a94de94e4fb471908b8cf798e62e411
