# [C] CVE-2015-2311

## Summary
Severity: Critical
Advisory: CVE-2015-2311
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-09
Source: https://osv.dev/vulnerability/CVE-2015-2311
Type: osv

## Details
Integer underflow in Sandstorm Cap'n Proto before 0.4.1.1 and 0.5.x before 0.5.1.1 might allow remote peers to cause a denial of service or possibly obtain sensitive information from memory or execute arbitrary code via a crafted message.

## References
- http://www.openwall.com/lists/oss-security/2015/03/17/3
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=780566
- https://github.com/capnproto/capnproto/blob/master/security-advisories/2015-03-02-1-c%2B%2B-integer-underflow.md
- https://github.com/capnproto/capnproto/commit/26bcceda72372211063d62aab7e45665faa83633
- http://www.openwall.com/lists/oss-security/2015/03/17/3
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=780566
