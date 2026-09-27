# [H] CVE-2019-11461

## Summary
Severity: High
Advisory: CVE-2019-11461
CVSS: 7.8 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-04-22
Source: https://osv.dev/vulnerability/CVE-2019-11461
Type: osv

## Details
An issue was discovered in GNOME Nautilus 3.30 prior to 3.30.6 and 3.32 prior to 3.32.1. A compromised thumbnailer may escape the bubblewrap sandbox used to confine thumbnailers by using the TIOCSTI ioctl to push characters into the input buffer of the thumbnailer's controlling terminal, allowing an attacker to escape the sandbox if the thumbnailer has a controlling terminal. This is due to improper filtering of the TIOCSTI ioctl on 64-bit systems, similar to CVE-2019-10063.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00088.html
- https://security.gentoo.org/glsa/201908-27
- https://gitlab.gnome.org/GNOME/nautilus/issues/987
