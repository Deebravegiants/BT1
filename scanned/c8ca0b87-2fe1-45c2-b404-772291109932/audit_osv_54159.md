# [H] CVE-2023-4055

## Summary
Severity: High
Advisory: CVE-2023-4055
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-08-01
Source: https://osv.dev/vulnerability/CVE-2023-4055
Type: osv

## Details
When the number of cookies per domain was exceeded in `document.cookie`, the actual cookie jar sent to the host was no longer consistent with expected cookie jar state. This could have caused requests to be sent with some cookies missing. This vulnerability affects Firefox < 116, Firefox ESR < 102.14, and Firefox ESR < 115.1.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00008.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00010.html
- https://www.mozilla.org/security/advisories/mfsa2023-29/
- https://www.mozilla.org/security/advisories/mfsa2023-30/
- https://www.mozilla.org/security/advisories/mfsa2023-31/
- https://www.debian.org/security/2023/dsa-5464
- https://www.debian.org/security/2023/dsa-5469
- https://bugzilla.mozilla.org/show_bug.cgi?id=1782561
