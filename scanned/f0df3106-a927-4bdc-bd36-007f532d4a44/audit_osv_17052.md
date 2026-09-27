# [H] CVE-2020-11728

## Summary
Severity: High
Advisory: CVE-2020-11728
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-15
Source: https://osv.dev/vulnerability/CVE-2020-11728
Type: osv

## Details
An issue was discovered in DAViCal Andrew's Web Libraries (AWL) through 0.60. Session management does not use a sufficiently hard-to-guess session key. Anyone who can guess the microsecond time (and the incrementing session_id) can impersonate a session.

## References
- https://usn.ubuntu.com/4539-1/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=956650
- https://lists.debian.org/debian-lts-announce/2020/04/msg00011.html
- https://www.debian.org/security/2020/dsa-4660
- https://gitlab.com/davical-project/awl/-/issues/19
