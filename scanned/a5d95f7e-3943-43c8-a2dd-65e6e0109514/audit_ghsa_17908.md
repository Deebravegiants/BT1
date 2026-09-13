# [M] Shopware race condition bypasses voucher restrictions

## Summary
Severity: Medium
Advisory: GHSA-27gv-mg7w-mm34
CVE: CVE-2025-7954
CWE: CWE-362
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-06
Source: https://github.com/advisories/GHSA-27gv-mg7w-mm34
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=0

## Details
A race condition vulnerability has been identified in Shopware's voucher system of Shopware v6.6.10.4 that allows attackers to bypass intended voucher restrictions and exceed usage limitations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-7954
- https://github.com/shopware/shopware/issues/11245
- https://github.com/shopware/shopware
- http://seclists.org/fulldisclosure/2025/Aug/17
