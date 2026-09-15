# [C] CVE-2024-11704

## Summary
Severity: Critical
Advisory: CVE-2024-11704
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-26
Source: https://osv.dev/vulnerability/CVE-2024-11704
Type: osv

## Details
A double-free issue could have occurred in `sec_pkcs7_decoder_start_decrypt()` when handling an error path. Under specific conditions, the same symmetric key could have been freed twice, potentially leading to memory corruption. This vulnerability affects Firefox < 133, Thunderbird < 133, Firefox ESR < 128.7, and Thunderbird < 128.7.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00005.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00006.html
- https://www.mozilla.org/security/advisories/mfsa2024-63/
- https://www.mozilla.org/security/advisories/mfsa2024-67/
- https://www.mozilla.org/security/advisories/mfsa2025-09/
- https://www.mozilla.org/security/advisories/mfsa2025-10/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1899402
