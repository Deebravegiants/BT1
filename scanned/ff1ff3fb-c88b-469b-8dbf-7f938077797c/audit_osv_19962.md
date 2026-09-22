# [M] CVE-2021-28650

## Summary
Severity: Medium
Advisory: CVE-2021-28650
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-17
Source: https://osv.dev/vulnerability/CVE-2021-28650
Type: osv

## Details
autoar-extractor.c in GNOME gnome-autoar before 0.3.1, as used by GNOME Shell, Nautilus, and other software, allows Directory Traversal during extraction because it lacks a check of whether a file's parent is a symlink in certain complex situations. NOTE: this issue exists because of an incomplete fix for CVE-2020-36241.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BN5TVQ7OHZEGY6AGFLAZWCVCI53RYNHQ/
- https://security.gentoo.org/glsa/202105-10
- https://gitlab.gnome.org/GNOME/gnome-autoar/-/commit/8109c368c6cfdb593faaf698c2bf5da32bb1ace4
