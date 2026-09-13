# [M] CVE-2022-33749

## Summary
Severity: Medium
Advisory: CVE-2022-33749
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/CVE-2022-33749
Type: osv

## Details
XAPI open file limit DoS It is possible for an unauthenticated client on the network to cause XAPI to hit its file-descriptor limit. This causes XAPI to be unable to accept new requests for other (trusted) clients, and blocks XAPI from carrying out any tasks that require the opening of file descriptors.

## References
- http://www.openwall.com/lists/oss-security/2022/10/11/4
- http://xenbits.xen.org/xsa/advisory-413.html
- https://security.gentoo.org/glsa/202402-07
- https://xenbits.xenproject.org/xsa/advisory-413.txt
- http://www.openwall.com/lists/oss-security/2022/10/11/4
- http://www.openwall.com/lists/oss-security/2022/10/11/4
- http://xenbits.xen.org/xsa/advisory-413.html
- https://xenbits.xenproject.org/xsa/advisory-413.txt
