# [C] CVE-2017-9214

## Summary
Severity: Critical
Advisory: CVE-2017-9214
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/CVE-2017-9214
Type: osv

## Details
In Open vSwitch (OvS) 2.7.0, while parsing an OFPT_QUEUE_GET_CONFIG_REPLY type OFP 1.0 message, there is a buffer over-read that is caused by an unsigned integer underflow in the function `ofputil_pull_queue_get_config_reply10` in `lib/ofp-util.c`.

## References
- https://access.redhat.com/errata/RHSA-2017:2418
- https://access.redhat.com/errata/RHSA-2017:2553
- https://access.redhat.com/errata/RHSA-2017:2648
- https://access.redhat.com/errata/RHSA-2017:2665
- https://access.redhat.com/errata/RHSA-2017:2692
- https://access.redhat.com/errata/RHSA-2017:2698
- https://access.redhat.com/errata/RHSA-2017:2727
- https://lists.debian.org/debian-lts-announce/2021/02/msg00032.html
- https://mail.openvswitch.org/pipermail/ovs-dev/2017-May/332711.html
