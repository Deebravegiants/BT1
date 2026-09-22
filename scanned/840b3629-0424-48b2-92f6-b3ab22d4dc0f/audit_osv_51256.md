# [M] CVE-2021-23953

## Summary
Severity: Medium
Advisory: CVE-2021-23953
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/CVE-2021-23953
Type: osv

## Details
If a user clicked into a specifically crafted PDF, the PDF reader could be confused into leaking cross-origin information, when said information is served as chunked data. This vulnerability affects Firefox < 85, Thunderbird < 78.7, and Firefox ESR < 78.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-03/
- https://www.mozilla.org/security/advisories/mfsa2021-04/
- https://www.mozilla.org/security/advisories/mfsa2021-05/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1683940
