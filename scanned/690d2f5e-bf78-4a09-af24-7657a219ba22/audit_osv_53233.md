# [M] CVE-2022-34472

## Summary
Severity: Medium
Advisory: CVE-2022-34472
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-34472
Type: osv

## Details
If there was a PAC URL set and the server that hosts the PAC was not reachable, OCSP requests would have been blocked, resulting in incorrect error pages being shown. This vulnerability affects Firefox < 102, Firefox ESR < 91.11, Thunderbird < 102, and Thunderbird < 91.11.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-26/
- https://www.mozilla.org/security/advisories/mfsa2022-24/
- https://www.mozilla.org/security/advisories/mfsa2022-25/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1770123
