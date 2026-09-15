# [C] Incorrect Authorization in Jenkins Kubernetes :: Pipeline :: Kubernetes Steps Plugin

## Summary
Severity: Critical
Advisory: GHSA-ccxh-j7hg-m5mr
CVE: CVE-2019-10417
CWE: CWE-183, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-ccxh-j7hg-m5mr
Type: github-advisory

## Affected
- Maven: `io.fabric8.pipeline:kubernetes-pipeline-steps` — affected >=0

## Details
Jenkins Kubernetes :: Pipeline :: Kubernetes Steps Plugin provides a custom whitelist for script security that allowed attackers to invoke arbitrary methods, bypassing typical sandbox protection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10417
- https://github.com/jenkinsci/kubernetes-pipeline-plugin/blob/master/kubernetes-steps
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-920%20(1)
- http://www.openwall.com/lists/oss-security/2019/09/25/3
