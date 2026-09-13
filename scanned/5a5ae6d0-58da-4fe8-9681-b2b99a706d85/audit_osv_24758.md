# [M] CVE-2023-26117

## Summary
Severity: Medium
Advisory: CVE-2023-26117
Aliases: GHSA-2qqx-w9hr-q5gx
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L/E:P)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/CVE-2023-26117
Type: osv

## Details
Versions of the package angular from 1.0.0 are vulnerable to Regular Expression Denial of Service (ReDoS) via the $resource service due to the usage of an insecure regular expression. Exploiting this vulnerability is possible by a large carefully-crafted input, which can result in catastrophic backtracking.

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OQWJLE5WE33WNMA54XSJIDXBRK2KL3XJ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UDKFLKJ6VZKL52AFVW2OVZRMJWHMW55K/
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-5406323
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBANGULAR-5406325
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-5406324
- https://security.snyk.io/vuln/SNYK-JS-ANGULAR-3373045
- https://stackblitz.com/edit/angularjs-vulnerability-resource-trailing-slashes-redos
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26117.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26117
