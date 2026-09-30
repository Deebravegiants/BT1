# [H] CVE-2017-1000111

## Summary
Severity: High
Advisory: CVE-2017-1000111
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-1000111
Type: osv

## Details
Linux kernel: heap out-of-bounds in AF_PACKET sockets. This new issue is analogous to previously disclosed CVE-2016-8655. In both cases, a socket option that changes socket state may race with safety checks in packet_set_ring. Previously with PACKET_VERSION. This time with PACKET_RESERVE. The solution is similar: lock the socket for the update. This issue may be exploitable, we did not investigate further. As this issue affects PF_PACKET sockets, it requires CAP_NET_RAW in the process namespace. But note that with user namespaces enabled, any process can create a namespace in which it has CAP_NET_RAW.

## References
- https://access.redhat.com/errata/RHSA-2017:2931
- https://access.redhat.com/errata/RHSA-2017:3200
- https://access.redhat.com/security/cve/cve-2017-1000111
- http://www.debian.org/security/2017/dsa-3981
- http://www.securityfocus.com/bid/100267
- http://www.securitytracker.com/id/1039132
- https://access.redhat.com/errata/RHSA-2017:2918
- https://access.redhat.com/errata/RHSA-2017:2930
