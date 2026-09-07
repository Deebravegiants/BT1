# [M] Croc may expose secret to local users

## Summary
Severity: Medium
Advisory: GHSA-7g3v-4ggr-xvjf
CVE: CVE-2023-43621
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-7g3v-4ggr-xvjf
Type: github-advisory

## Affected
- Go: `github.com/schollz/croc/v9` — affected >=0 <9.6.16

## Details
An issue was discovered in Croc before 9.6.16. The shared secret, located on a command line, can be read by local users who list all processes and their arguments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43621
- https://github.com/schollz/croc/issues/598
- https://github.com/schollz/croc/pull/701
- https://github.com/schollz/croc/commit/863dabb93a271f41b3431c4384357e1856a69533
- https://github.com/schollz/croc
- https://www.openwall.com/lists/oss-security/2023/09/08/2
- http://www.openwall.com/lists/oss-security/2023/09/21/5
