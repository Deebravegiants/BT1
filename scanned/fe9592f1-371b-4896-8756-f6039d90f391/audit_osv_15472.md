# [M] CVE-2019-16680

## Summary
Severity: Medium
Advisory: CVE-2019-16680
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2019-09-21
Source: https://osv.dev/vulnerability/CVE-2019-16680
Type: osv

## Details
An issue was discovered in GNOME file-roller before 3.29.91. It allows a single ./../ path traversal via a filename contained in a TAR archive, possibly overwriting a file during extraction.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1767594
- https://lists.debian.org/debian-lts-announce/2019/09/msg00032.html
- https://seclists.org/bugtraq/2019/Sep/57
- https://usn.ubuntu.com/4139-1/
- https://www.debian.org/security/2019/dsa-4537
- https://bugzilla.gnome.org/show_bug.cgi?id=794337
- https://gitlab.gnome.org/GNOME/file-roller/commit/57268e51e59b61c9e3125eb0f65551c7084297e2
- https://gitlab.gnome.org/GNOME/file-roller/commit/e8fb3e24dae711e4fb0d6777e0016cdda8787bc1
