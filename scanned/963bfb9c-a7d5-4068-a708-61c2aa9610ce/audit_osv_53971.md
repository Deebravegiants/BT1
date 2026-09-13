# [C] CVE-2023-34416

## Summary
Severity: Critical
Advisory: CVE-2023-34416
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-19
Source: https://osv.dev/vulnerability/CVE-2023-34416
Type: osv

## Details
Memory safety bugs present in Firefox 113, Firefox ESR 102.11, and Thunderbird 102.12. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox ESR < 102.12, Firefox < 114, and Thunderbird < 102.12.

## References
- https://security.gentoo.org/glsa/202312-03
- https://security.gentoo.org/glsa/202401-10
- https://www.mozilla.org/security/advisories/mfsa2023-19/
- https://www.mozilla.org/security/advisories/mfsa2023-20/
- https://www.mozilla.org/security/advisories/mfsa2023-21/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1752703%2C1818394%2C1826875%2C1827340%2C1827655%2C1828065%2C1830190%2C1830206%2C1830795%2C1833339
