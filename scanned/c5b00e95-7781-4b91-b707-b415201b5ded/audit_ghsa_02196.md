# [M] Cross-site scripting in feehicms

## Summary
Severity: Medium
Advisory: GHSA-f8pv-x7h8-687v
CVE: CVE-2020-19709
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-f8pv-x7h8-687v
Type: github-advisory

## Affected
- Packagist: `feehi/feehicms` — affected >=0

## Details
Insufficient filtering of the tag parameters in feehicms 0.1.3 allows attackers to execute arbitrary web or HTML via a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-19709
- https://github.com/liufee/feehicms/issues/2
- https://github.com/liufee/feehicms
