# [M] Jenkins OpenShift Login Plugin vulnerable to Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-35gf-xjgf-96c5
CVE: CVE-2023-37947
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-35gf-xjgf-96c5
Type: github-advisory

## Affected
- Maven: `org.openshift.jenkins:openshift-login` — affected >=0 <1.1.0.230.v5d7030b

## Details
Jenkins OpenShift Login Plugin 1.1.0.227.v27e08dfb_1a_20 and earlier improperly determines that a redirect URL after login is legitimately pointing to Jenkins.

This allows attackers to perform phishing attacks by having users go to a Jenkins URL that will forward them to a different site after successful authentication.

OpenShift Login Plugin 1.1.0.230.v5d7030b_f5432 only redirects to relative (Jenkins) URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37947
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-2999
- http://www.openwall.com/lists/oss-security/2023/07/12/2
