# [C] BIT-jenkins-2021-21685

## Summary
Severity: Critical
Advisory: BIT-jenkins-2021-21685
Aliases: CVE-2021-21685, GHSA-58xm-mxjf-254g
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2021-21685
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.319.0

## Details
Jenkins LTS 2.303.2 and earlier does not check agent-to-controller access to create parent directories in FilePath#mkdirs.

## References
- http://www.openwall.com/lists/oss-security/2021/11/04/3
- https://www.jenkins.io/security/advisory/2021-11-04/#SECURITY-2455
- https://nvd.nist.gov/vuln/detail/CVE-2021-21685
