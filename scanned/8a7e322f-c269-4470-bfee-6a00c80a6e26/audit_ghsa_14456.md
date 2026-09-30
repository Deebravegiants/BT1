# [M] angular vulnerable to regular expression denial of service via the angular.copy() utility

## Summary
Severity: Medium
Advisory: GHSA-2vrf-hf26-jrp5
CVE: CVE-2023-26116
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-03-30
Source: https://github.com/advisories/GHSA-2vrf-hf26-jrp5
Type: github-advisory

## Affected
- npm: `angular` — affected >=0

## Details
All versions of the package angular are vulnerable to Regular Expression Denial of Service (ReDoS) via the angular.copy() utility function due to the usage of an insecure regular expression. Exploiting this vulnerability is possible by a large carefully-crafted input, which can result in catastrophic backtracking.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26116
- https://github.com/angular/angular.js
- https://lists.debian.org/debian-lts-announce/2025/07/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OQWJLE5WE33WNMA54XSJIDXBRK2KL3XJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UDKFLKJ6VZKL52AFVW2OVZRMJWHMW55K
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-5406320
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBANGULAR-5406322
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-5406321
- https://security.snyk.io/vuln/SNYK-JS-ANGULAR-3373044
- https://stackblitz.com/edit/angularjs-vulnerability-angular-copy-redos
