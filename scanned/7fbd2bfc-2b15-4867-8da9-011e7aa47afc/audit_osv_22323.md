# [H] CVE-2022-25182

## Summary
Severity: High
Advisory: CVE-2022-25182
Aliases: GHSA-7rcw-fwfh-2h2g
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-15
Source: https://osv.dev/vulnerability/CVE-2022-25182
Type: osv

## Details
A sandbox bypass vulnerability in Jenkins Pipeline: Shared Groovy Libraries Plugin 552.vd9cc05b8a2e1 and earlier allows attackers with Item/Configure permission to execute arbitrary code on the Jenkins controller JVM using specially crafted library names if a global Pipeline library is already configured.

## References
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2422
