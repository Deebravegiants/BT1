# [M] Broadleaf vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-3862-fmr3-4f3h
CVE: CVE-2023-33725
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-06-21
Source: https://github.com/advisories/GHSA-3862-fmr3-4f3h
Type: github-advisory

## Affected
- Maven: `org.broadleafcommerce:broadleaf` — affected >=5.0.0-GA <6.2.7-GA

## Details
Broadleaf 5.x and 6.x (including 5.2.25-GA and 6.2.6-GA) was discovered to contain a cross-site scripting (XSS) vulnerability via a customer signup with a crafted email address. This is fixed in 6.2.7-GA.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33725
- https://github.com/BroadleafCommerce/BroadleafCommerce
- https://github.com/Contrast-Security-OSS/Burptrast/tree/main/docs/CVE-2023-33725
