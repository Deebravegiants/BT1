# [H] CVE-2019-11502

## Summary
Severity: High
Advisory: CVE-2019-11502
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-24
Source: https://osv.dev/vulnerability/CVE-2019-11502
Type: osv

## Details
snap-confine in snapd before 2.38 incorrectly set the ownership of a snap application to the uid and gid of the first calling user. Consequently, that user had unintended access to a private /tmp directory.

## References
- http://www.openwall.com/lists/oss-security/2019/04/25/7
- https://github.com/snapcore/snapd/commit/bdbfeebef03245176ae0dc323392bb0522a339b1
- https://www.openwall.com/lists/oss-security/2019/04/18/4
