# [M] CVE-2019-10332

## Summary
Severity: Medium
Advisory: CVE-2019-10332
Aliases: GHSA-66r6-rvv9-9x6m
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2019-06-11
Source: https://osv.dev/vulnerability/CVE-2019-10332
Type: osv

## Details
A missing permission check in Jenkins ElectricFlow Plugin 1.1.5 and earlier in Configuration#doTestConnection allowed users with Overall/Read access to connect to an attacker-specified URL using attacker-specified credentials.

## References
- http://www.openwall.com/lists/oss-security/2019/06/11/1
- http://www.securityfocus.com/bid/108747
- https://jenkins.io/security/advisory/2019-06-11/#SECURITY-1410%20%281%29
