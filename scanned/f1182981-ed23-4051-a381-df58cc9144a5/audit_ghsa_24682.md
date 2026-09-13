# [M] Jenkins does not Restrict Reserved Names Allowing for Privilege Escalation 

## Summary
Severity: Medium
Advisory: GHSA-37wm-28rm-56vw
CVE: CVE-2015-1810
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-37wm-28rm-56vw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.597 <1.600
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.596.1

## Details
The HudsonPrivateSecurityRealm class in Jenkins before 1.600 and LTS before 1.596.1 does not restrict access to reserved names when using the "Jenkins' own user database" setting, which allows remote attackers to gain privileges by creating a reserved name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1810
- https://access.redhat.com/errata/RHSA-2016:0070
- https://bugzilla.redhat.com/show_bug.cgi?id=1205627
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2015-02-27
- http://rhn.redhat.com/errata/RHSA-2015-1844.html
