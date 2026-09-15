# [C] CVE-2023-4056

## Summary
Severity: Critical
Advisory: CVE-2023-4056
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-01
Source: https://osv.dev/vulnerability/CVE-2023-4056
Type: osv

## Details
Memory safety bugs present in Firefox 115, Firefox ESR 115.0, Firefox ESR 102.13, Thunderbird 115.0, and Thunderbird 102.13. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 116, Firefox ESR < 102.14, and Firefox ESR < 115.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-31/
- https://lists.debian.org/debian-lts-announce/2023/08/msg00008.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00010.html
- https://www.debian.org/security/2023/dsa-5464
- https://www.debian.org/security/2023/dsa-5469
- https://www.mozilla.org/security/advisories/mfsa2023-29/
- https://www.mozilla.org/security/advisories/mfsa2023-30/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1820587%2C1824634%2C1839235%2C1842325%2C1843847
