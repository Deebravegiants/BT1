# [H] Sealos billing system permission control defect

## Summary
Severity: High
Advisory: GHSA-vpxf-q44g-w34w
CVE: CVE-2023-36815
CWE: CWE-287, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-vpxf-q44g-w34w
Type: github-advisory

## Affected
- Go: `github.com/labring/sealos` — affected >=0

## Details
### Summary

There is a permission flaw in the Sealos billing system, which allows users to control the recharge resource account. sealos. io/v1/Payment, resulting in the ability to recharge any amount of 1 RMB.

### Details

The reason is that sealos is in arrears. Egg pain, we can't create a terminal anymore. Let's charge for it:

Then it was discovered that the charging interface had returned all resource information. Unfortunately, based on previous vulnerability experience, the namespace of this custom resource is still under the current user's control and may have permission to correct it.

### PoC
disable by publish

### Impact

+ sealos public cloud user
+ CWE-287 Improper Authentication

## References
- https://github.com/labring/sealos/security/advisories/GHSA-vpxf-q44g-w34w
- https://nvd.nist.gov/vuln/detail/CVE-2023-36815
- https://github.com/labring/sealos
