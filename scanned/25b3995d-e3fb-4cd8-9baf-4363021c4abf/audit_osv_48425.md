# [H] CVE-2017-7558

## Summary
Severity: High
Advisory: CVE-2017-7558
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2017-7558
Type: osv

## Details
A kernel data leak due to an out-of-bound read was found in the Linux kernel in inet_diag_msg_sctp{,l}addr_fill() and sctp_get_sctp_info() functions present since version 4.7-rc1 through version 4.13. A data leak happens when these functions fill in sockaddr data structures used to export socket's diagnostic information. As a result, up to 100 bytes of the slab data could be leaked to a userspace.

## References
- http://www.securityfocus.com/bid/100466
- https://www.debian.org/security/2017/dsa-3981
- http://seclists.org/oss-sec/2017/q3/338
- http://www.securitytracker.com/id/1039221
- https://access.redhat.com/errata/RHSA-2017:2918
- https://access.redhat.com/errata/RHSA-2017:2930
- https://access.redhat.com/errata/RHSA-2017:2931
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7558
- https://marc.info/?l=linux-netdev&m=150348777122761&w=2
