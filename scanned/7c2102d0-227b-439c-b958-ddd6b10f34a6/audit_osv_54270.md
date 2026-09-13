# [M] CVE-2023-4580

## Summary
Severity: Medium
Advisory: CVE-2023-4580
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-09-11
Source: https://osv.dev/vulnerability/CVE-2023-4580
Type: osv

## Details
Push notifications stored on disk in private browsing mode were not being encrypted potentially allowing the leak of sensitive information. This vulnerability affects Firefox < 117, Firefox ESR < 115.2, and Thunderbird < 115.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-34/
- https://www.mozilla.org/security/advisories/mfsa2023-36/
- https://www.mozilla.org/security/advisories/mfsa2023-38/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1843046
