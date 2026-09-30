# [H] CVE-2022-38473

## Summary
Severity: High
Advisory: CVE-2022-38473
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-38473
Type: osv

## Details
A cross-origin iframe referencing an XSLT document would inherit the parent domain's permissions (such as microphone or camera access). This vulnerability affects Thunderbird < 102.2, Thunderbird < 91.13, Firefox ESR < 91.13, Firefox ESR < 102.2, and Firefox < 104.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-33/
- https://www.mozilla.org/security/advisories/mfsa2022-34/
- https://www.mozilla.org/security/advisories/mfsa2022-35/
- https://www.mozilla.org/security/advisories/mfsa2022-36/
- https://www.mozilla.org/security/advisories/mfsa2022-37/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1771685
