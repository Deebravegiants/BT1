# [M] CVE-2026-18750

## Summary
Severity: Medium
Advisory: CVE-2026-18750
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-18750
Type: osv

## Details
vinny/views.py: (ModifyEmailNotifications)	IDOR: view fetches VinceCommEmail by raw pk from URL and toggles email_function/name without checking the record's contact belongs to the requesting group-admin. Lets a vendor admin flip notification routing (or read email/name) for another vendor's contact.

## References
- https://certcc.github.com/CERTCC/VINCE/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18750.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18750
- https://github.com/CERTCC/VINCE/pull/235
