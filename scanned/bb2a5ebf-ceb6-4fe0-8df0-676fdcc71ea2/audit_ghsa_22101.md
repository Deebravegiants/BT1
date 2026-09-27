# [M] Improper Limitation of a Pathname to a Restricted Directory in plexus-archiver

## Summary
Severity: Medium
Advisory: GHSA-hcxq-x77q-3469
CVE: CVE-2018-1002200
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-hcxq-x77q-3469
Type: github-advisory

## Affected
- Maven: `org.codehaus.plexus:plexus-archiver` — affected >=0 <3.6.0

## Details
plexus-archiver before 3.6.0 is vulnerable to directory traversal, allowing attackers to write to arbitrary files via a ../ (dot dot slash) in an archive entry that is mishandled during extraction. This vulnerability is also known as 'Zip-Slip'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1002200
- https://github.com/codehaus-plexus/plexus-archiver/pull/87
- https://github.com/codehaus-plexus/plexus-archiver/commit/f8f4233508193b70df33759ae9dc6154d69c2ea8
- https://access.redhat.com/errata/RHSA-2018:1836
- https://access.redhat.com/errata/RHSA-2018:1837
- https://github.com/codehaus-plexus/plexus-archiver
- https://github.com/snyk/zip-slip-vulnerability
- https://snyk.io/research/zip-slip-vulnerability
- https://snyk.io/vuln/SNYK-JAVA-ORGCODEHAUSPLEXUS-31680
- https://www.debian.org/security/2018/dsa-4227
