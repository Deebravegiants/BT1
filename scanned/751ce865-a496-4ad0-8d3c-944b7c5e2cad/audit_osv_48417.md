# [M] CVE-2017-7519

## Summary
Severity: Medium
Advisory: CVE-2017-7519
CVSS: 4.4 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-7519
Type: osv

## Details
In Ceph, a format string flaw was found in the way libradosstriper parses input from user. A user could crash an application or service using the libradosstriper library.

## References
- http://www.securityfocus.com/bid/99075
- https://www.debian.org/security/2018/dsa-4339
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7519
