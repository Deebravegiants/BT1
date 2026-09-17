# [H] CVE-2024-3857

## Summary
Severity: High
Advisory: CVE-2024-3857
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-3857
Type: osv

## Details
The JIT created incorrect code for arguments in certain cases. This led to potential use-after-free crashes during garbage collection. This vulnerability affects Firefox < 125, Firefox ESR < 115.10, and Thunderbird < 115.10.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-20/
- https://lists.debian.org/debian-lts-announce/2024/04/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/04/msg00013.html
- https://www.mozilla.org/security/advisories/mfsa2024-18/
- https://www.mozilla.org/security/advisories/mfsa2024-19/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1886683
