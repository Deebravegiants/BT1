# [C] CVE-2021-33574

## Summary
Severity: Critical
Advisory: CVE-2021-33574
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-25
Source: https://osv.dev/vulnerability/CVE-2021-33574
Type: osv

## Details
The mq_notify function in the GNU C Library (aka glibc) versions 2.32 and 2.33 has a use-after-free. It may use the notification thread attributes object (passed through its struct sigevent parameter) after it has been freed by the caller, leading to a denial of service (application crash) or possibly unspecified other impact.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KJYYIMDDYOHTP2PORLABTOHYQYYREZDD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RBUUWUGXVILQXVWEOU7N42ICHPJNAEUP/
- https://lists.debian.org/debian-lts-announce/2022/10/msg00021.html
- https://security.gentoo.org/glsa/202107-07
- https://security.netapp.com/advisory/ntap-20210629-0005/
- https://sourceware.org/bugzilla/show_bug.cgi?id=27896
- https://sourceware.org/bugzilla/show_bug.cgi?id=27896#c1
