# [H] CVE-2014-2277

## Summary
Severity: High
Advisory: CVE-2014-2277
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2017-10-17
Source: https://osv.dev/vulnerability/CVE-2014-2277
Type: osv

## Details
The make_temporary_filename function in perltidy 20120701-1 and earlier allows local users to obtain sensitive information or write to arbitrary files via a symlink attack, related to use of the tmpnam function.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2014-March/130464.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-March/130479.html
- http://www.openwall.com/lists/oss-security/2014/03/09/1
- http://www.securityfocus.com/bid/66139
- https://bugzilla.redhat.com/show_bug.cgi?id=1074720
- https://exchange.xforce.ibmcloud.com/vulnerabilities/92104
- http://www.openwall.com/lists/oss-security/2014/03/09/1
- http://lists.fedoraproject.org/pipermail/package-announce/2014-March/130464.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-March/130479.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1074720
