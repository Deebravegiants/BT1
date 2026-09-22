# [M] BIT-golang-2020-14039

## Summary
Severity: Medium
Advisory: BIT-golang-2020-14039
Aliases: CVE-2020-14039, GO-2021-0223
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2020-14039
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.14.0 <1.14.5

## Details
In Go before 1.13.13 and 1.14.x before 1.14.5, Certificate.Verify may lack a check on the VerifyOptions.KeyUsages EKU requirements (if VerifyOptions.Roots equals nil and the installation is on Windows). Thus, X.509 certificate verification is incomplete.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00077.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00082.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00030.html
- https://groups.google.com/forum/#%21forum/golang-announce
- https://groups.google.com/forum/#%21topic/golang-announce/XZNfaiwgt2w
- https://security.netapp.com/advisory/ntap-20200731-0005/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-14039
