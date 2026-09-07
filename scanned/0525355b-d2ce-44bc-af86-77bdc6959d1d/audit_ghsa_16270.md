# [M] sanitize-html Information Exposure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rm97-x556-q36h
CVE: CVE-2024-21501
CWE: CWE-200, CWE-538
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-24
Source: https://github.com/advisories/GHSA-rm97-x556-q36h
Type: github-advisory

## Affected
- npm: `sanitize-html` — affected >=0 <2.12.1

## Details
Versions of the package sanitize-html before 2.12.1 are vulnerable to Information Exposure when used on the backend and with the style attribute allowed, allowing enumeration of files in the system (including project dependencies). An attacker could exploit this vulnerability to gather details about the file system structure and dependencies of the targeted server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21501
- https://github.com/apostrophecms/sanitize-html/pull/650
- https://github.com/apostrophecms/sanitize-html/commit/c5dbdf77fe8b836d3bf4554ea39edb45281ec0b4
- https://gist.github.com/Slonser/8b4d061abe6ee1b2e10c7242987674cf
- https://github.com/apostrophecms/apostrophe/discussions/4436
- https://github.com/apostrophecms/sanitize-html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4EB5JPYRCTS64EA5AMV3INHDPI6I4AW7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/P4I5X6V3LYUNBMZ5YOW4BV427TH3IK4S
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-6276557
- https://security.snyk.io/vuln/SNYK-JS-SANITIZEHTML-6256334
