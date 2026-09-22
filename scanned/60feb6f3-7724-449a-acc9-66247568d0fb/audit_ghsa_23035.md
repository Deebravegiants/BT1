# [M] Improper authorization in Jenkins Job and Node Ownership Plugin

## Summary
Severity: Medium
Advisory: GHSA-72x3-c7jc-q35x
CVE: CVE-2018-1000107
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-72x3-c7jc-q35x
Type: github-advisory

## Affected
- Maven: `com.synopsys.jenkinsci:ownership` — affected >=0 <0.12.0

## Details
An improper authorization vulnerability exists in Jenkins Job and Node Ownership Plugin 0.11.0 and earlier in 
```
OwnershipDescription.java, 
JobOwnerJobProperty.java, 
and OwnerNodeProperty.java 
```
that allow an attacker with Job/Configure or Computer/Configure permission and without Ownership related permissions to override ownership metadata.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000107
- https://github.com/jenkinsci/ownership-plugin/commit/42487df17cd272e504d3cd3e09abb4904f80dba2
- https://github.com/jenkinsci/ownership-plugin/blob/2908d3c0e23a34919449838304090210640c67c1/CHANGELOG.md?plain=1#L26
- https://jenkins.io/security/advisory/2018-02-26/#SECURITY-498
