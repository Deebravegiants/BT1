# [H] CVE-2018-1000500

## Summary
Severity: High
Advisory: CVE-2018-1000500
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-1000500
Type: osv

## Details
Busybox contains a Missing SSL certificate validation vulnerability in The "busybox wget" applet that can result in arbitrary code execution. This attack appear to be exploitable via Simply download any file over HTTPS using "busybox wget https://compromised-domain.com/important-file".

## References
- https://usn.ubuntu.com/4531-1/
- http://lists.busybox.net/pipermail/busybox/2018-May/086462.html
- https://git.busybox.net/busybox/commit/?id=45fa3f18adf57ef9d743038743d9c90573aeeb91
