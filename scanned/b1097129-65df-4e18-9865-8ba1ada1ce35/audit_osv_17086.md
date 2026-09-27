# [H] CVE-2020-12100

## Summary
Severity: High
Advisory: CVE-2020-12100
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-12
Source: https://osv.dev/vulnerability/CVE-2020-12100
Type: osv

## Details
In Dovecot before 2.3.11.3, uncontrolled recursion in submission, lmtp, and lda allows remote attackers to cause a denial of service (resource consumption) via a crafted e-mail message with deeply nested MIME parts.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4AAX2MJEULPVSRZOBX3PNPFSYP4FM4TT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EYZU6CHA3VMYYAUCMHSCCQKJEVEIKPQ2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XKKAL3OMG76ZZ7CIEMQP2K6KCTD2RAKE/
- http://seclists.org/fulldisclosure/2021/Jan/18
- http://www.openwall.com/lists/oss-security/2021/01/04/3
- https://dovecot.org/security
- https://lists.debian.org/debian-lts-announce/2020/08/msg00024.html
- https://security.gentoo.org/glsa/202009-02
- https://usn.ubuntu.com/4456-1/
- https://usn.ubuntu.com/4456-2/
- https://www.debian.org/security/2020/dsa-4745
- http://www.openwall.com/lists/oss-security/2020/08/12/1
