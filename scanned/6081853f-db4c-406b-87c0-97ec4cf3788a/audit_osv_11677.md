# [C] CVE-2017-9265

## Summary
Severity: Critical
Advisory: CVE-2017-9265
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-29
Source: https://osv.dev/vulnerability/CVE-2017-9265
Type: osv

## Details
In Open vSwitch (OvS) v2.7.0, there is a buffer over-read while parsing the group mod OpenFlow message sent from the controller in `lib/ofp-util.c` in the function `ofputil_pull_ofp15_group_mod`.

## References
- https://access.redhat.com/errata/RHSA-2017:2418
- https://access.redhat.com/errata/RHSA-2017:2553
- https://access.redhat.com/errata/RHSA-2017:2648
- https://access.redhat.com/errata/RHSA-2017:2665
- https://access.redhat.com/errata/RHSA-2017:2692
- https://access.redhat.com/errata/RHSA-2017:2698
- https://access.redhat.com/errata/RHSA-2017:2727
- https://mail.openvswitch.org/pipermail/ovs-dev/2017-May/332965.html
