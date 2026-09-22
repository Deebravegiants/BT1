# [H] CVE-2021-43537

## Summary
Severity: High
Advisory: CVE-2021-43537
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-12-08
Source: https://osv.dev/vulnerability/CVE-2021-43537
Type: osv

## Details
An incorrect type conversion of sizes from 64bit to 32bit integers allowed an attacker to corrupt memory leading to a potentially exploitable crash. This vulnerability affects Thunderbird < 91.4.0, Firefox ESR < 91.4.0, and Firefox < 95.

## References
- https://security.gentoo.org/glsa/202208-14
- https://www.debian.org/security/2022/dsa-5034
- https://www.mozilla.org/security/advisories/mfsa2021-52/
- https://www.mozilla.org/security/advisories/mfsa2021-53/
- https://lists.debian.org/debian-lts-announce/2022/01/msg00001.html
- https://www.debian.org/security/2021/dsa-5026
- https://www.mozilla.org/security/advisories/mfsa2021-54/
- https://lists.debian.org/debian-lts-announce/2021/12/msg00030.html
- https://security.gentoo.org/glsa/202202-03
- https://bugzilla.mozilla.org/show_bug.cgi?id=1738237
