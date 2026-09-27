# [H] CVE-2019-8308

## Summary
Severity: High
Advisory: CVE-2019-8308
CVSS: 8.2 (CVSS:3.0/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2019-02-12
Source: https://osv.dev/vulnerability/CVE-2019-8308
Type: osv

## Details
Flatpak before 1.0.7, and 1.1.x and 1.2.x before 1.2.3, exposes /proc in the apply_extra script sandbox, which allows attackers to modify a host-side executable file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00088.html
- https://access.redhat.com/errata/RHSA-2019:0375
- https://github.com/flatpak/flatpak/releases/tag/1.0.7
- https://github.com/flatpak/flatpak/releases/tag/1.2.3
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=922059
