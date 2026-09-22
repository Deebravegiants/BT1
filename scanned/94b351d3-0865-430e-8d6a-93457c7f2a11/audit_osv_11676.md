# [C] CVE-2017-9264

## Summary
Severity: Critical
Advisory: CVE-2017-9264
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-29
Source: https://osv.dev/vulnerability/CVE-2017-9264
Type: osv

## Details
In lib/conntrack.c in the firewall implementation in Open vSwitch (OvS) 2.6.1, there is a buffer over-read while parsing malformed TCP, UDP, and IPv6 packets in the functions `extract_l3_ipv6`, `extract_l4_tcp`, and `extract_l4_udp` that can be triggered remotely.

## References
- https://access.redhat.com/errata/RHSA-2017:2418
- https://access.redhat.com/errata/RHSA-2017:2648
- https://access.redhat.com/errata/RHSA-2017:2727
- https://mail.openvswitch.org/pipermail/ovs-dev/2017-March/329323.html
