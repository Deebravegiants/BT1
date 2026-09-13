# [M] CVE-2020-14954

## Summary
Severity: Medium
Advisory: CVE-2020-14954
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-06-21
Source: https://osv.dev/vulnerability/CVE-2020-14954
Type: osv

## Details
Mutt before 1.14.4 and NeoMutt before 2020-06-19 have a STARTTLS buffering issue that affects IMAP, SMTP, and POP3. When a server sends a "begin TLS" response, the client reads additional data (e.g., from a man-in-the-middle attacker) and evaluates it in a TLS context, aka "response injection."

## References
- http://www.mutt.org/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EFMEILCBKMZRRZDMUGWLVN4PQQ4VTAZE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K3LXFVPTLK4PNHL6MPKJNJQJ25CH7GLQ/
- http://lists.mutt.org/pipermail/mutt-announce/Week-of-Mon-20200615/000023.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00070.html
- https://github.com/neomutt/neomutt/releases/tag/20200619
- https://lists.debian.org/debian-lts-announce/2020/06/msg00039.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00040.html
- https://security.gentoo.org/glsa/202007-57
- https://usn.ubuntu.com/4403-1/
- https://www.debian.org/security/2020/dsa-4707
- https://www.debian.org/security/2020/dsa-4708
- https://gitlab.com/muttmua/mutt/-/issues/248
- https://github.com/neomutt/neomutt/commit/fb013ec666759cb8a9e294347c7b4c1f597639cc
- https://gitlab.com/muttmua/mutt/-/commit/c547433cdf2e79191b15c6932c57f1472bfb5ff4
