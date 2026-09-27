# [M] Path traversal vulnerability in Blue Ocean Plugin

## Summary
Severity: Medium
Advisory: GHSA-vq7j-6pcq-f48p
CVE: CVE-2020-2254
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vq7j-6pcq-f48p
Type: github-advisory

## Affected
- Maven: `io.jenkins.blueocean:blueocean` — affected >=0 <1.23.3

## Details
Blue Ocean Plugin 1.23.2 and earlier provides an undocumented feature flag, `blueocean.features.GIT_READ_SAVE_TYPE`, that when set to the value `clone` allows an attacker with Item/Configure or Item/Create permission to read arbitrary files on the Jenkins controller file system.

Blue Ocean Plugin 1.23.3 no longer includes this feature and redirects existing usage to a safer alternative.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2254
- https://github.com/jenkinsci/blueocean-plugin/commit/f0dd4b68d62ac3c3c85012d6eb0c92bcebf85e12
- https://github.com/jenkinsci/blueocean-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1956
- http://www.openwall.com/lists/oss-security/2020/09/16/3
