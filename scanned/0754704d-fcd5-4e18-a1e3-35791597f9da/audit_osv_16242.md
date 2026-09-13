# [M] CVE-2019-3814

## Summary
Severity: Medium
Advisory: CVE-2019-3814
CVSS: 6.8 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/CVE-2019-3814
Type: osv

## Details
It was discovered that Dovecot before versions 2.2.36.1 and 2.3.4.1 incorrectly handled client certificates. A remote attacker in possession of a valid certificate with an empty username field could possibly use this issue to impersonate other users.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4XLI55NGRDTGMVOPYFCPPFNPA5VKYSSY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QHFZ5OWRIZGIWZJ5PTNVWWZNLLNH4XYS/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00067.html
- https://access.redhat.com/errata/RHSA-2019:3467
- https://security.gentoo.org/glsa/201904-19
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3814
- https://www.dovecot.org/list/dovecot/2019-February/114575.html
