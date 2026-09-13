# [H] CVE-2016-4478

## Summary
Severity: High
Advisory: CVE-2016-4478
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-13
Source: https://osv.dev/vulnerability/CVE-2016-4478
Type: osv

## Details
Buffer overflow in the xmlrpc_char_encode function in modules/transport/xmlrpc/xmlrpclib.c in Atheme before 7.2.7 allows remote attackers to cause a denial of service via vectors related to XMLRPC response encoding.

## References
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00061.html
- http://www.openwall.com/lists/oss-security/2016/05/02/2
- http://www.openwall.com/lists/oss-security/2016/05/03/1
- http://www.debian.org/security/2016/dsa-3586
- https://github.com/atheme/atheme/commit/87580d767868360d2fed503980129504da84b63e
