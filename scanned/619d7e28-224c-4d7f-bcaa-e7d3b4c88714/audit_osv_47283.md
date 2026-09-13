# [M] CVE-2016-2121

## Summary
Severity: Medium
Advisory: CVE-2016-2121
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/CVE-2016-2121
Type: osv

## Details
A permissions flaw was found in redis, which sets weak permissions on certain files and directories that could potentially contain sensitive information. A local, unprivileged user could possibly use this flaw to access unauthorized system information.

## References
- http://www.securityfocus.com/bid/94111
- https://access.redhat.com/errata/RHSA-2017:3226
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-2121
