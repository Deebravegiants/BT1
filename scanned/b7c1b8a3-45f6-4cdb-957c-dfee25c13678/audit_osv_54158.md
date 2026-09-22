# [M] CVE-2023-4053

## Summary
Severity: Medium
Advisory: CVE-2023-4053
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2023-08-01
Source: https://osv.dev/vulnerability/CVE-2023-4053
Type: osv

## Details
A website could have obscured the full screen notification by using a URL with a scheme handled by an external program, such as a mailto URL. This could have led to user confusion and possible spoofing attacks. This vulnerability affects Firefox < 116, Firefox ESR < 115.2, and Thunderbird < 115.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-29/
- https://www.mozilla.org/security/advisories/mfsa2023-36/
- https://www.mozilla.org/security/advisories/mfsa2023-38/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1839079
