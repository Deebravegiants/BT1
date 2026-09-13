# [C] CVE-2020-28984

## Summary
Severity: Critical
Advisory: CVE-2020-28984
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-23
Source: https://osv.dev/vulnerability/CVE-2020-28984
Type: osv

## Details
prive/formulaires/configurer_preferences.php in SPIP before 3.2.8 does not properly validate the couleur, display, display_navigation, display_outils, imessage, and spip_ecran parameters.

## References
- https://git.spip.net/spip/spip/compare/v3.2.7...v3.2.8
- https://lists.debian.org/debian-lts-announce/2020/12/msg00036.html
- https://www.debian.org/security/2020/dsa-4798
- https://git.spip.net/spip/spip/commit/ae4267eba1022dabc12831ddb021c5d6e09040f8
