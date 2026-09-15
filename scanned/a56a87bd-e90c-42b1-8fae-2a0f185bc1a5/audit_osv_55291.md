# [H] CVE-2025-26696

## Summary
Severity: High
Advisory: CVE-2025-26696
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2025-03-10
Source: https://osv.dev/vulnerability/CVE-2025-26696
Type: osv

## Details
Certain crafted MIME email messages that claimed to contain an encrypted OpenPGP message, which instead contained an OpenPGP signed message, were wrongly shown as being encrypted. This vulnerability affects Thunderbird < 136 and Thunderbird < 128.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2025-17/
- https://www.mozilla.org/security/advisories/mfsa2025-18/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1864205
