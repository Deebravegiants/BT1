# [H] CVE-2016-10377

## Summary
Severity: High
Advisory: CVE-2016-10377
CVSS: 8.8 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-29
Source: https://osv.dev/vulnerability/CVE-2016-10377
Type: osv

## Details
In Open vSwitch (OvS) 2.5.0, a malformed IP packet can cause the switch to read past the end of the packet buffer due to an unsigned integer underflow in `lib/flow.c` in the function `miniflow_extract`, permitting remote bypass of the access control list enforced by the switch.

## References
- https://mail.openvswitch.org/pipermail/ovs-dev/2016-July/319503.html
