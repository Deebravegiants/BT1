# [H] CVE-2018-11102

## Summary
Severity: High
Advisory: CVE-2018-11102
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-15
Source: https://osv.dev/vulnerability/CVE-2018-11102
Type: osv

## Details
An issue was discovered in Libav 12.3. A read access violation in the mov_probe function in libavformat/mov.c allows remote attackers to cause a denial of service (application crash), as demonstrated by avconv.

## References
- https://lists.debian.org/debian-lts-announce/2019/09/msg00000.html
- https://docs.google.com/document/d/18xCwfxMSJiQ9ruQSVaO8-jlcobDjFiYXWOaw31V37xo/edit
- https://bugzilla.libav.org/show_bug.cgi?id=1128
