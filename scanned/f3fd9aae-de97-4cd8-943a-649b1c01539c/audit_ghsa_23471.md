# [H] Jenkins discloses project names via fingerprints

## Summary
Severity: High
Advisory: GHSA-8pqx-3rxx-f5pm
CVE: CVE-2015-5317
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N/E:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8pqx-3rxx-f5pm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.625.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.626 <1.638

## Details
The Fingerprints pages in Jenkins before 1.638 and LTS before 1.625.2 might allow remote attackers to obtain sensitive job and build name information via a direct request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5317
- https://github.com/jenkinsci/jenkins/commit/0594c4cbccd24d4883fc0150e8fc511c9da63eb4
- https://access.redhat.com/errata/RHSA-2016:0070
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2015-11-11
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2015-5317
- http://rhn.redhat.com/errata/RHSA-2016-0489.html
