# [M] BIT-jenkins-2020-2102

## Summary
Severity: Medium
Advisory: BIT-jenkins-2020-2102
Aliases: CVE-2020-2102, GHSA-fj6f-6933-839j
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2020-2102
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.218.1

## Details
Jenkins 2.218 and earlier, LTS 2.204.1 and earlier used a non-constant time comparison function when validating an HMAC.

## References
- http://www.openwall.com/lists/oss-security/2020/01/29/1
- https://access.redhat.com/errata/RHBA-2020:0402
- https://access.redhat.com/errata/RHBA-2020:0675
- https://access.redhat.com/errata/RHSA-2020:0681
- https://access.redhat.com/errata/RHSA-2020:0683
- https://jenkins.io/security/advisory/2020-01-29/#SECURITY-1660
- https://nvd.nist.gov/vuln/detail/CVE-2020-2102
