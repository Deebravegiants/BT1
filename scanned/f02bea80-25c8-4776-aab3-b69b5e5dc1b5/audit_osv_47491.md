# [H] CVE-2016-6866

## Summary
Severity: High
Advisory: CVE-2016-6866
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-6866
Type: osv

## Details
slock allows attackers to bypass the screen lock via vectors involving an invalid password hash, which triggers a NULL pointer dereference and crash.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2FYPV6QQPPYBL3Z2BYNYEJB67FSC55OR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RZPEJQNVODYSI4WQXM5GQKXRO7TPK2VG/
- http://www.openwall.com/lists/oss-security/2016/08/18/22
- http://www.openwall.com/lists/oss-security/2016/08/18/24
- http://www.securityfocus.com/bid/92546
- http://s1m0n.dft-labs.eu/files/slock/slock.txt
- http://git.suckless.org/slock/commit/?id=d8bec0f6fdc8a246d78cb488a0068954b46fcb29
