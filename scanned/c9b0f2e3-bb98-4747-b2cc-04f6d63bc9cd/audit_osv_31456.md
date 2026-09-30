# [H] CVE-2025-11699

## Summary
Severity: High
Advisory: CVE-2025-11699
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N)
Published: 2025-12-01
Source: https://osv.dev/vulnerability/CVE-2025-11699
Type: osv

## Details
nopCommerce v4.70 and prior, and version 4.80.3, does not invalidate session cookies after logout or session termination, allowing an attacker who has a 
a valid session cookie access to privileged endpoints (such as /admin) even after the legitimate user has logged out, enabling session hijacking. Any version above 4.70 that is not 4.80.3 fixes the vulnerability.

## References
- https://seclists.org/fulldisclosure/2025/Aug/14
- https://www.kb.cert.org/vuls/id/633103
- https://www.nopcommerce.com/en/release-notes?srsltid=AfmBOoravPKjN19pm_XZbXZ7GvPhkt8cxlK6794BJRZlY5RxJU_yNoTT
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/11xxx/CVE-2025-11699.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-11699
- https://github.com/nopSolutions/nopCommerce/issues/7044
