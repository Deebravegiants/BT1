# [H] Jenkins allows Deserialization of Untrusted Data via an XML File

## Summary
Severity: High
Advisory: GHSA-45rg-g72w-r393
CVE: CVE-2016-0792
CWE: CWE-20, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-45rg-g72w-r393
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.643 <1.650
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.642.2

## Details
Multiple unspecified API endpoints in Jenkins before 1.650 and LTS before 1.642.2 allow remote authenticated users to execute arbitrary code via serialized data in an XML file, related to XStream and groovy.util.Expando.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0792
- https://github.com/jenkinsci/jenkins/commit/7f202f0317e60cd3160f61467b8558f864f83f41
- https://access.redhat.com/errata/RHSA-2016:0711
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2016-02-24
- https://www.contrastsecurity.com/security-influencers/serialization-must-die-act-2-xstream
- https://www.exploit-db.com/exploits/42394
- https://www.exploit-db.com/exploits/43375
- http://rhn.redhat.com/errata/RHSA-2016-1773.html
