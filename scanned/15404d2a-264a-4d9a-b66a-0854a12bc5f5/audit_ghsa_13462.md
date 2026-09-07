# [H] Jenkins OpenShift Login Plugin session fixation vulnerability

## Summary
Severity: High
Advisory: GHSA-rwg5-2pv9-633w
CVE: CVE-2023-37946
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-rwg5-2pv9-633w
Type: github-advisory

## Affected
- Maven: `org.openshift.jenkins:openshift-login` — affected >=0 <1.1.0.230.v5d7030b

## Details
Jenkins OpenShift Login Plugin 1.1.0.227.v27e08dfb_1a_20 and earlier does not invalidate the existing session on login.

This allows attackers to use social engineering techniques to gain administrator access to Jenkins.

OpenShift Login Plugin 1.1.0.230.v5d7030b_f5432 invalidates the existing session on login.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37946
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-2998
- http://www.openwall.com/lists/oss-security/2023/07/12/2
