# [M] CVE-2020-28896

## Summary
Severity: Medium
Advisory: CVE-2020-28896
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-11-23
Source: https://osv.dev/vulnerability/CVE-2020-28896
Type: osv

## Details
Mutt before 2.0.2 and NeoMutt before 2020-11-20 did not ensure that $ssl_force_tls was processed if an IMAP server's initial server response was invalid. The connection was not properly closed, and the code could continue attempting to authenticate. This could result in authentication credentials being exposed on an unencrypted connection, or to a machine-in-the-middle.

## References
- https://github.com/neomutt/neomutt/releases/tag/20201120
- https://lists.debian.org/debian-lts-announce/2020/11/msg00048.html
- https://security.gentoo.org/glsa/202101-32
- https://github.com/neomutt/neomutt/commit/9c36717a3e2af1f2c1b7242035455ec8112b4b06
- https://gitlab.com/muttmua/mutt/-/commit/04b06aaa3e0cc0022b9b01dbca2863756ebbf59a
- https://gitlab.com/muttmua/mutt/-/commit/d92689088dfe80a290ec836e292376e2d9984f8f
