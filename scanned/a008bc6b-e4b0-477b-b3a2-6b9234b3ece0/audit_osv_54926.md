# [H] CVE-2024-6609

## Summary
Severity: High
Advisory: CVE-2024-6609
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/CVE-2024-6609
Type: osv

## Details
When almost out-of-memory an elliptic curve key which was never allocated could have been freed again. This vulnerability affects Firefox < 128 and Thunderbird < 128.

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00028.html
- https://www.mozilla.org/security/advisories/mfsa2024-29/
- https://www.mozilla.org/security/advisories/mfsa2024-32/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1839258
