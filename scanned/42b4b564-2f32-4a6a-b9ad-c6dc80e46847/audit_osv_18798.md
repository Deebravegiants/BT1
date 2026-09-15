# [M] CVE-2020-36241

## Summary
Severity: Medium
Advisory: CVE-2020-36241
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-02-05
Source: https://osv.dev/vulnerability/CVE-2020-36241
Type: osv

## Details
autoar-extractor.c in GNOME gnome-autoar through 0.2.4, as used by GNOME Shell, Nautilus, and other software, allows Directory Traversal during extraction because it lacks a check of whether a file's parent is a symlink to a directory outside of the intended extraction location.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BN5TVQ7OHZEGY6AGFLAZWCVCI53RYNHQ/
- https://security.gentoo.org/glsa/202105-10
- https://gitlab.gnome.org/GNOME/gnome-autoar/-/issues/7
- https://gitlab.gnome.org/GNOME/gnome-autoar/-/commit/adb067e645732fdbe7103516e506d09eb6a54429
