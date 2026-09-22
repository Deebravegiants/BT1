# [M] CVE-2019-16393

## Summary
Severity: Medium
Advisory: CVE-2019-16393
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-09-17
Source: https://osv.dev/vulnerability/CVE-2019-16393
Type: osv

## Details
SPIP before 3.1.11 and 3.2 before 3.2.5 mishandles redirect URLs in ecrire/inc/headers.php with a %0D, %0A, or %20 character.

## References
- https://lists.debian.org/debian-lts-announce/2019/10/msg00038.html
- https://seclists.org/bugtraq/2019/Sep/40
- https://usn.ubuntu.com/4536-1/
- https://www.debian.org/security/2019/dsa-4532
- https://core.spip.net/issues/4362
- https://git.spip.net/SPIP/spip/commit/0b832408b0aabd5b94a81e261e9413c0f31a19f1
- https://blog.spip.net/Mise-a-jour-CRITIQUE-de-securite-Sortie-de-SPIP-3-2-5-et-SPIP-3-1-11.html
