# [H] Path Traversal in OWASP Dependency-Check

## Summary
Severity: High
Advisory: GHSA-hcwx-7q5v-vc67
CVE: CVE-2018-12036
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-hcwx-7q5v-vc67
Type: github-advisory

## Affected
- Maven: `org.owasp:dependency-check-maven` — affected >=0 <3.2.0

## Details
OWASP Dependency-Check before 3.2.0 allows attackers to write to arbitrary files via a crafted archive that holds directory traversal filenames.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12036
- https://github.com/jeremylong/DependencyCheck
- https://github.com/jeremylong/DependencyCheck/blob/master/RELEASE_NOTES.md#version-320-2018-05-21
- https://github.com/snyk/zip-slip-vulnerability
