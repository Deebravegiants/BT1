# [M] CVE-2022-28286

## Summary
Severity: Medium
Advisory: CVE-2022-28286
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-28286
Type: osv

## Details
Due to a layout change, iframe contents could have been rendered outside of its border. This could have led to user confusion or spoofing attacks. This vulnerability affects Thunderbird < 91.8, Firefox < 99, and Firefox ESR < 91.8.

## References
- https://bugzilla.mozilla.org/show_bug.cgi?id=1735265
- https://www.mozilla.org/security/advisories/mfsa2022-13/
- https://www.mozilla.org/security/advisories/mfsa2022-14/
- https://www.mozilla.org/security/advisories/mfsa2022-15/
