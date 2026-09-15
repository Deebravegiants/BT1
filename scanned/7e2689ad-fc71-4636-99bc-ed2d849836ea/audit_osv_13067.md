# [M] CVE-2018-17206

## Summary
Severity: Medium
Advisory: CVE-2018-17206
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-19
Source: https://osv.dev/vulnerability/CVE-2018-17206
Type: osv

## Details
An issue was discovered in Open vSwitch (OvS) 2.7.x through 2.7.6. The decode_bundle function inside lib/ofp-actions.c is affected by a buffer over-read issue during BUNDLE action decoding.

## References
- https://access.redhat.com/errata/RHSA-2018:3500
- https://access.redhat.com/errata/RHSA-2019:0053
- https://access.redhat.com/errata/RHSA-2019:0081
- https://lists.debian.org/debian-lts-announce/2021/02/msg00032.html
- https://usn.ubuntu.com/3873-1/
- https://github.com/openvswitch/ovs/commit/9237a63c47bd314b807cda0bd2216264e82edbe8
