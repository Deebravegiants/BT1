# [M] LibreNMS affected by reflected xss via email field 

## Summary
Severity: Medium
Advisory: GHSA-gqx7-99jw-6fpr
CVE: CVE-2026-26987
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-gqx7-99jw-6fpr
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <26.2.0

## Details
### Summary
reflected xss via email field 

### Details
 1. visit `http://127.0.0.1/settings/alerting/email`
 2. in the email address input but this payload 
 `<img src=1 onerror=alert(document.cookie)>` 
3. notice the alert 
### PoC
- video attached with the report
https://github.com/user-attachments/assets/c1b443f5-85c6-4545-b04f-def06d82b42e


### Impact
can lead to ATO

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-gqx7-99jw-6fpr
- https://nvd.nist.gov/vuln/detail/CVE-2026-26987
- https://github.com/librenms/librenms/pull/19038
- https://github.com/librenms/librenms/commit/8e626b38ef92e240532cdac2ac7e38706a71208b
- https://github.com/librenms/librenms
- https://github.com/librenms/librenms/releases/tag/26.2.0
