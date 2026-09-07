# [H] Unauthorized view fragment access in Jenkins

## Summary
Severity: High
Advisory: GHSA-p3rc-946h-8cf5
CVE: CVE-2022-34175
CWE: CWE-693, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-p3rc-946h-8cf5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.335 <2.356

## Details
Jenkins uses the Stapler web framework to render its UI views. These views are frequently composed of several view fragments, enabling plugins to extend existing views with more content.

Before [SECURITY-534](https://www.jenkins.io/security/advisory/2019-07-17/#SECURITY-534) was fixed in Jenkins 2.186 and LTS 2.176.2, attackers could in some cases directly access a view fragment containing sensitive information, bypassing any permission checks in the corresponding view.

In Jenkins 2.335 through 2.355 (both inclusive), the protection added for SECURITY-534 is disabled for some views. As a result, attackers could in very limited cases directly access a view fragment containing sensitive information, bypassing any permission checks in the corresponding view.

As of publication, the Jenkins security team is unaware of any vulnerable view fragment across the Jenkins plugin ecosystem.

Jenkins 2.356 restores the protection for affected views.

No Jenkins LTS release is affected by this issue, as it was not present in Jenkins 2.332.x and fixed in the 2.346.x line before 2.346.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34175
- https://github.com/jenkinsci/jenkins/commit/37bd66a43ad561f670db7440f493d69518741d27
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2777
