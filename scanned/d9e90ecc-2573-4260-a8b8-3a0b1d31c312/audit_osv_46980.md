# [M] CVE-2015-8629

## Summary
Severity: Medium
Advisory: CVE-2015-8629
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-02-13
Source: https://osv.dev/vulnerability/CVE-2015-8629
Type: osv

## Details
The xdr_nullstring function in lib/kadm5/kadm_rpc_xdr.c in kadmind in MIT Kerberos 5 (aka krb5) before 1.13.4 and 1.14.x before 1.14.1 does not verify whether '\0' characters exist as expected, which allows remote authenticated users to obtain sensitive information or cause a denial of service (out-of-bounds read) via a crafted string.

## References
- http://krbdev.mit.edu/rt/Ticket/Display.html?id=8341
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00059.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00110.html
- http://rhn.redhat.com/errata/RHSA-2016-0493.html
- http://rhn.redhat.com/errata/RHSA-2016-0532.html
- http://www.debian.org/security/2016/dsa-3466
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securityfocus.com/bid/82801
- http://www.securitytracker.com/id/1034914
- https://github.com/krb5/krb5/commit/df17a1224a3406f57477bcd372c61e04c0e5a5bb
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00059.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00110.html
- https://github.com/krb5/krb5/commit/df17a1224a3406f57477bcd372c61e04c0e5a5bb
