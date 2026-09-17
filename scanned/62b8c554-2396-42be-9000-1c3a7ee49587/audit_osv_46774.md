# [C] CVE-2015-2310

## Summary
Severity: Critical
Advisory: CVE-2015-2310
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-08-09
Source: https://osv.dev/vulnerability/CVE-2015-2310
Type: osv

## Details
Integer overflow in layout.c++ in Sandstorm Cap'n Proto before 0.4.1.1 and 0.5.x before 0.5.1.1 allows remote peers to cause a denial of service or possibly obtain sensitive information from memory via a crafted message, related to pointer validation.

## References
- http://www.openwall.com/lists/oss-security/2015/03/17/3
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=780565
- https://github.com/capnproto/capnproto/blob/master/security-advisories/2015-03-02-0-c%2B%2B-integer-overflow.md
- https://github.com/capnproto/capnproto/commit/f343f0dbd0a2e87f17cd74f14186ed73e3fbdbfa
- http://www.openwall.com/lists/oss-security/2015/03/17/3
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=780565
