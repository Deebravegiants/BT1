# [H] Jenkins vulnerable to stored cross site scripting in the I:helpIcon component

## Summary
Severity: High
Advisory: GHSA-xpvp-h73c-m9rq
CVE: CVE-2022-41224
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-xpvp-h73c-m9rq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.367 <2.370

## Details
Jenkins 2.367 through 2.369 (both inclusive) does not escape tooltips of the `l:helpIcon` UI component used for some help icons on the Jenkins web UI, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control tooltips for this component.

As of publication, the Jenkins security team is unaware of any exploitable help icon/tooltip in Jenkins core or plugins published by the Jenkins project. The vast majority of help icons use the `l:help` component instead of l:helpIcon. The few known instances of `l:helpIcon` do not have user-controllable tooltip contents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41224
- https://github.com/jenkinsci/jenkins/commit/84f41d2921023374dedb7d6f12d47eaf7790b7eb
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2886
