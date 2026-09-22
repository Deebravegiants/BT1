# [H] CVE-2019-1003024

## Summary
Severity: High
Advisory: CVE-2019-1003024
Aliases: GHSA-jgpm-2862-q5m8
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-20
Source: https://osv.dev/vulnerability/CVE-2019-1003024
Type: osv

## Details
A sandbox bypass vulnerability exists in Jenkins Script Security Plugin 1.52 and earlier in RejectASTTransformsCustomizer.java that allows attackers with Overall/Read permission to provide a Groovy script to an HTTP endpoint that can result in arbitrary code execution on the Jenkins master JVM.

## References
- http://www.securityfocus.com/bid/107295
- https://access.redhat.com/errata/RHSA-2019:0739
- https://jenkins.io/security/advisory/2019-02-19/#SECURITY-1320
