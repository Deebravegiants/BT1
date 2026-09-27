# [M] Jenkins improperly ensures trust separation

## Summary
Severity: Medium
Advisory: GHSA-66cr-6whx-732p
CVE: CVE-2014-3665
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-66cr-6whx-732p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.587

## Details
Jenkins prior to 1.587 and LTS before 1.580.1 do not properly ensure trust separation between a master and slaves, which might allow remote attackers to execute arbitrary code on the master by leveraging access to the slave.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3665
- https://access.redhat.com/errata/RHBA-2014:1630
- https://access.redhat.com/security/cve/CVE-2014-3665
- https://bugzilla.redhat.com/show_bug.cgi?id=1147767
- https://wiki.jenkins-ci.org/display/JENKINS/Slave+To+Master+Access+Control
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2014-10-30
