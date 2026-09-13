# [H] CVE-2017-11421

## Summary
Severity: High
Advisory: CVE-2017-11421
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-18
Source: https://osv.dev/vulnerability/CVE-2017-11421
Type: osv

## Details
gnome-exe-thumbnailer before 0.9.5 is prone to a VBScript Injection when generating thumbnails for MSI files, aka the "Bad Taste" issue. There is a local attack if the victim uses the GNOME Files file manager, and navigates to a directory containing a .msi file with VBScript code in its filename.

## References
- http://www.securityfocus.com/bid/99922
- http://news.dieweltistgarnichtso.net/posts/gnome-thumbnailer-msi-fail.html
- https://bugs.debian.org/868705
- https://github.com/gnome-exe-thumbnailer/gnome-exe-thumbnailer/commit/1d8e3102dd8fd23431ae6127d14a236da6b4a4a5
