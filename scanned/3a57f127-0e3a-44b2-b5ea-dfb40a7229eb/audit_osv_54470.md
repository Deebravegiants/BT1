# [H] CVE-2023-6858

## Summary
Severity: High
Advisory: CVE-2023-6858
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-12-19
Source: https://osv.dev/vulnerability/CVE-2023-6858
Type: osv

## Details
Firefox was susceptible to a heap buffer overflow in `nsTextFragment` due to insufficient OOM handling. This vulnerability affects Firefox ESR < 115.6, Thunderbird < 115.6, and Firefox < 121.

## References
- https://security.gentoo.org/glsa/202401-10
- https://www.mozilla.org/security/advisories/mfsa2023-54/
- https://www.mozilla.org/security/advisories/mfsa2023-55/
- https://lists.debian.org/debian-lts-announce/2023/12/msg00020.html
- https://lists.debian.org/debian-lts-announce/2023/12/msg00021.html
- https://www.debian.org/security/2023/dsa-5581
- https://www.debian.org/security/2023/dsa-5582
- https://www.mozilla.org/security/advisories/mfsa2023-56/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1826791
