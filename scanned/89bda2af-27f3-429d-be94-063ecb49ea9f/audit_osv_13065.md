# [M] CVE-2018-17204

## Summary
Severity: Medium
Advisory: CVE-2018-17204
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2018-09-19
Source: https://osv.dev/vulnerability/CVE-2018-17204
Type: osv

## Details
An issue was discovered in Open vSwitch (OvS) 2.7.x through 2.7.6, affecting parse_group_prop_ntr_selection_method in lib/ofp-util.c. When decoding a group mod, it validates the group type and command after the whole group mod has been decoded. The OF1.5 decoder, however, tries to use the type and command earlier, when it might still be invalid. This causes an assertion failure (via OVS_NOT_REACHED). ovs-vswitchd does not enable support for OpenFlow 1.5 by default.

## References
- https://access.redhat.com/errata/RHSA-2018:3500
- https://access.redhat.com/errata/RHSA-2019:0053
- https://access.redhat.com/errata/RHSA-2019:0081
- https://lists.debian.org/debian-lts-announce/2021/02/msg00032.html
- https://usn.ubuntu.com/3873-1/
- https://github.com/openvswitch/ovs/commit/4af6da3b275b764b1afe194df6499b33d2bf4cde
