# [M] CVE-2021-38509

## Summary
Severity: Medium
Advisory: CVE-2021-38509
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2021-12-08
Source: https://osv.dev/vulnerability/CVE-2021-38509
Type: osv

## Details
Due to an unusual sequence of attacker-controlled events, a Javascript alert() dialog with arbitrary (although unstyled) contents could be displayed over top an uncontrolled webpage of the attacker's choosing. This vulnerability affects Firefox < 94, Thunderbird < 91.3, and Firefox ESR < 91.3.

## References
- https://www.debian.org/security/2022/dsa-5034
- https://www.mozilla.org/security/advisories/mfsa2021-48/
- https://www.mozilla.org/security/advisories/mfsa2021-49/
- https://www.mozilla.org/security/advisories/mfsa2021-50/
- https://lists.debian.org/debian-lts-announce/2021/12/msg00030.html
- https://security.gentoo.org/glsa/202202-03
- https://security.gentoo.org/glsa/202208-14
- https://lists.debian.org/debian-lts-announce/2022/01/msg00001.html
- https://www.debian.org/security/2021/dsa-5026
- https://bugzilla.mozilla.org/show_bug.cgi?id=1718571
