# [M] Eclipse JGit XML External Entity (XXE) Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vrpq-qp53-qv56
CVE: CVE-2025-4949
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:A/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2025-05-21
Source: https://github.com/advisories/GHSA-vrpq-qp53-qv56
Type: github-advisory

## Affected
- Maven: `org.eclipse.jgit:org.eclipse.jgit` — affected >=7.2.0.202503040940-r <7.2.1.202505142326-r
- Maven: `org.eclipse.jgit:org.eclipse.jgit` — affected >=7.1.0.202411261347-r <7.1.1.202505221757-r
- Maven: `org.eclipse.jgit:org.eclipse.jgit` — affected >=7.0.0.202409031743-r <7.0.1.202505221510-r
- Maven: `org.eclipse.jgit:org.eclipse.jgit` — affected >=6.1.0.202203080745-r <6.10.1.202505221210-r
- Maven: `org.eclipse.jgit:org.eclipse.jgit` — affected >=6.0.0.202110060947-m1 <6.0.0.202111291000-r
- Maven: `org.eclipse.jgit:org.eclipse.jgit` — affected >=0 <5.13.4.202507202350-r

## Details
In Eclipse JGit versions 7.2.0.202503040940-r and older, the ManifestParser class used by the repo command and the AmazonS3 class used to implement the experimental amazons3 git transport protocol allowing to store git pack files in an Amazon S3 bucket, are vulnerable to XML External Entity (XXE) attacks when parsing XML files. This vulnerability can lead to information disclosure, denial of service, and other security issues.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4949
- https://github.com/eclipse-jgit/jgit
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/64
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/281
- https://projects.eclipse.org/projects/technology.jgit/releases/5.13.4
- https://projects.eclipse.org/projects/technology.jgit/releases/5.13.5
- https://projects.eclipse.org/projects/technology.jgit/releases/6.10.1
- https://projects.eclipse.org/projects/technology.jgit/releases/7.0.1
- https://projects.eclipse.org/projects/technology.jgit/releases/7.1.1
- https://projects.eclipse.org/projects/technology.jgit/releases/7.2.1
