# [H] Croc sender may send dangerous new files to receiver

## Summary
Severity: High
Advisory: GHSA-ppjh-xp5v-46wc
CVE: CVE-2023-43619
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-ppjh-xp5v-46wc
Type: github-advisory

## Affected
- Go: `github.com/schollz/croc/v9` — affected >=0 <9.6.16

## Details
An issue was discovered in Croc before 9.6.16. A sender may send dangerous new files to a receiver, such as executable content or a `.ssh/authorized_keys` file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43619
- https://github.com/schollz/croc/issues/593
- https://github.com/schollz/croc/pull/697
- https://github.com/schollz/croc/commit/3f12f75fae2e844c555ec01eeba0b8474938e93a
- https://github.com/schollz/croc
- https://www.openwall.com/lists/oss-security/2023/09/08/2
- http://www.openwall.com/lists/oss-security/2023/09/21/5
