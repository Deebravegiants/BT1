# [M] toy-blog administrative token leaked through the command line parameter

## Summary
Severity: Medium
Advisory: CVE-2024-39314
Aliases: GHSA-q8g2-c3x5-gp89
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-07-01
Source: https://osv.dev/vulnerability/CVE-2024-39314
Type: osv

## Details
toy-blog is a headless content management system implementation. Starting in version 0.4.3 and prior to version 0.5.0, the administrative password was leaked through the command line parameter. The problem was patched in version 0.5.0. As a workaround, pass `--read-bearer-token-from-stdin` to the launch arguments and feed the token from the standard input in version 0.4.14 or later. Earlier versions do not have this workaround.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39314.json
- https://github.com/KisaragiEffective/toy-blog/security/advisories/GHSA-q8g2-c3x5-gp89
- https://nvd.nist.gov/vuln/detail/CVE-2024-39314
- https://github.com/KisaragiEffective/toy-blog/commit/4d003e46a944d8f44ea02c63f4beefa4cbe1f4f7
