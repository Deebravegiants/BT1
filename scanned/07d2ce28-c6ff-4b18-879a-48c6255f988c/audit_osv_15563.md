# [C] CVE-2019-17266

## Summary
Severity: Critical
Advisory: CVE-2019-17266
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-06
Source: https://osv.dev/vulnerability/CVE-2019-17266
Type: osv

## Details
libsoup from versions 2.65.1 until 2.68.1 have a heap-based buffer over-read because soup_ntlm_parse_challenge() in soup-auth-ntlm.c does not properly check an NTLM message's length before proceeding with a memcpy.

## References
- https://www.mail-archive.com/debian-bugs-dist%40lists.debian.org/msg1705054.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=941912
- https://github.com/Kirin-say/Vulnerabilities/blob/master/CVE-2019-17266_POC.md
- https://gitlab.gnome.org/GNOME/libsoup/commit/88b7dff4467f4151afae244ea7d1223753cd05ab
- https://gitlab.gnome.org/GNOME/libsoup/commit/f8a54ac85eec2008c85393f331cdd251af8266ad
- https://security-tracker.debian.org/tracker/CVE-2019-17266
- https://usn.ubuntu.com/4152-1/
- https://gitlab.gnome.org/GNOME/libsoup/issues/173
