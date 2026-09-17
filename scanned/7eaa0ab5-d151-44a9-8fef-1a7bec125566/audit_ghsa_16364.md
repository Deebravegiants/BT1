# [H] angular vulnerable to super-linear runtime due to backtracking

## Summary
Severity: High
Advisory: GHSA-4w4v-5hc9-xrr2
CVE: CVE-2024-21490
CWE: CWE-1333
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-10
Source: https://github.com/advisories/GHSA-4w4v-5hc9-xrr2
Type: github-advisory

## Affected
- npm: `angular` — affected >=1.3.0
- Maven: `org.webjars.npm:angular` — affected >=1.3.0
- Maven: `org.webjars.bower:angular` — affected >=1.3.0

## Details
This affects versions of the package angular from 1.3.0. A regular expression used to split the value of the ng-srcset directive is vulnerable to super-linear runtime due to backtracking. With a large carefully-crafted input, this can result in catastrophic backtracking and cause a denial of service. 


**Note:**

This package is EOL and will not receive any updates to address this issue. Users should migrate to [@angular/core](https://www.npmjs.com/package/@angular/core).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21490
- https://github.com/angular/angular.js
- https://lists.debian.org/debian-lts-announce/2025/07/msg00005.html
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-6241746
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-6241747
- https://security.snyk.io/vuln/SNYK-JS-ANGULAR-6091113
- https://stackblitz.com/edit/angularjs-vulnerability-ng-srcset-redos
- https://support.herodevs.com/hc/en-us/articles/25715686953485-CVE-2024-21490-AngularJS-Regular-Expression-Denial-of-Service-ReDoS
