# [M] Frappe LMS SQL Injection Issue on People Page

## Summary
Severity: Medium
Advisory: CVE-2023-42807
Aliases: GHSA-wvq3-3wvp-6x63
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-09-21
Source: https://osv.dev/vulnerability/CVE-2023-42807
Type: osv

## Details
Frappe LMS is an open source learning management system. In versions 1.0.0 and prior, on the People Page of LMS, there was an SQL Injection vulnerability. The issue has been fixed in the `main` branch. Users won't face this issue if they are using the latest main branch of the app.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42807.json
- https://github.com/frappe/lms/security/advisories/GHSA-wvq3-3wvp-6x63
- https://nvd.nist.gov/vuln/detail/CVE-2023-42807
