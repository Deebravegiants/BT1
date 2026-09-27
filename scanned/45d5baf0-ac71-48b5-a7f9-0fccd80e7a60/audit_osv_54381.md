# [M] CVE-2023-5388

## Summary
Severity: Medium
Advisory: CVE-2023-5388
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2024-03-19
Source: https://osv.dev/vulnerability/CVE-2023-5388
Type: osv

## Details
NSS was susceptible to a timing side-channel attack when performing RSA decryption. This attack could potentially allow an attacker to recover the private data. This vulnerability affects Firefox < 124, Firefox ESR < 115.9, and Thunderbird < 115.9.

## References
- https://lists.debian.org/debian-lts-announce/2024/03/msg00010.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00028.html
- https://www.mozilla.org/security/advisories/mfsa2024-12/
- https://www.mozilla.org/security/advisories/mfsa2024-13/
- https://www.mozilla.org/security/advisories/mfsa2024-14/
- https://lists.debian.org/debian-lts-announce/2024/03/msg00022.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1780432
