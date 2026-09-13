# [H] Croc sender may place ANSI or CSI escape sequences in filename to attach receiver's terminal device

## Summary
Severity: High
Advisory: GHSA-364c-vvqx-446c
CVE: CVE-2023-43620
CWE: CWE-116
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-364c-vvqx-446c
Type: github-advisory

## Affected
- Go: `github.com/schollz/croc/v9` — affected >=0 <9.6.16

## Details
An issue was discovered in Croc before 9.6.16. A sender may place ANSI or CSI escape sequences in a filename to attack the terminal device of a receiver.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43620
- https://github.com/schollz/croc/issues/595
- https://github.com/schollz/croc/pull/697
- https://github.com/schollz/croc/commit/3f12f75fae2e844c555ec01eeba0b8474938e93a
- https://github.com/schollz/croc
- https://www.openwall.com/lists/oss-security/2023/09/08/2
- http://www.openwall.com/lists/oss-security/2023/09/21/5
