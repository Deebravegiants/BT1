# [M] Missing Authentication for Critical Function in Saleor

## Summary
Severity: Medium
Advisory: GHSA-rgcm-rpq9-9cgr
CVE: CVE-2020-7964
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-07-28
Source: https://github.com/advisories/GHSA-rgcm-rpq9-9cgr
Type: github-advisory

## Affected
- PyPI: `saleor` — affected >=2.0.0 <2.9.1

## Details
An issue was discovered in Mirumee Saleor 2.x before 2.9.1. Incorrect access control in the checkoutCustomerAttach mutations allows attackers to attach their checkouts to any user ID and consequently leak user data (e.g., name, address, and previous orders of any other customer).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7964
- https://github.com/mirumee/saleor/commit/233b8890c60fa6d90daf99e4d90fea85867732c3
- https://github.com/mirumee/saleor/releases/tag/2.9.1
