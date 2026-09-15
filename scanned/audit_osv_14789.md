# [H] CVE-2019-11455

## Summary
Severity: High
Advisory: CVE-2019-11455
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-04-22
Source: https://osv.dev/vulnerability/CVE-2019-11455
Type: osv

## Details
A buffer over-read in Util_urlDecode in util.c in Tildeslash Monit before 5.25.3 allows a remote authenticated attacker to retrieve the contents of adjacent memory via manipulation of GET or POST parameters. The attacker can also cause a denial of service (application outage).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HZQDHRSKTEX5MSYXNCGFTUSFGANBARHX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L475QJMFFI2QV5QEHAKKPVX6QX6ECUL6/
- https://lists.debian.org/debian-lts-announce/2019/04/msg00028.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00018.html
- https://bitbucket.org/tildeslash/monit/commits/f12d0cdb42d4e74dffe1525d4062c815c48ac57a
- https://usn.ubuntu.com/3971-1/
- https://github.com/dzflack/exploits/blob/master/macos/monit_dos.py
- https://github.com/dzflack/exploits/blob/master/unix/monit_buffer_overread.py
