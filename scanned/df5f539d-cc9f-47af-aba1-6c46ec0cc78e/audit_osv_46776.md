# [H] CVE-2015-2312

## Summary
Severity: High
Advisory: CVE-2015-2312
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-09
Source: https://osv.dev/vulnerability/CVE-2015-2312
Type: osv

## Details
Sandstorm Cap'n Proto before 0.4.1.1 and 0.5.x before 0.5.1.1 allows remote peers to cause a denial of service (CPU and possibly general resource consumption) via a list with a large number of elements.

## References
- http://www.openwall.com/lists/oss-security/2015/03/17/3
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=780567
- https://github.com/capnproto/capnproto/blob/master/security-advisories/2015-03-02-2-all-cpu-amplification.md
- https://github.com/capnproto/capnproto/commit/104870608fde3c698483fdef6b97f093fc15685d
- http://www.openwall.com/lists/oss-security/2015/03/17/3
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=780567
