# [H] CVE-2018-11396

## Summary
Severity: High
Advisory: CVE-2018-11396
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-23
Source: https://osv.dev/vulnerability/CVE-2018-11396
Type: osv

## Details
ephy-session.c in libephymain.so in GNOME Web (aka Epiphany) through 3.28.2.1 allows remote attackers to cause a denial of service (application crash) via JavaScript code that triggers access to a NULL URL, as demonstrated by a crafted window.open call.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00043.html
- https://bugzilla.gnome.org/show_bug.cgi?id=795740
