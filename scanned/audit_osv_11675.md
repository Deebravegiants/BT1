# [M] CVE-2017-9263

## Summary
Severity: Medium
Advisory: CVE-2017-9263
CVSS: 6.5 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-29
Source: https://osv.dev/vulnerability/CVE-2017-9263
Type: osv

## Details
In Open vSwitch (OvS) 2.7.0, while parsing an OpenFlow role status message, there is a call to the abort() function for undefined role status reasons in the function `ofp_print_role_status_message` in `lib/ofp-print.c` that may be leveraged toward a remote DoS attack by a malicious switch.

## References
- https://access.redhat.com/errata/RHSA-2017:2418
- https://access.redhat.com/errata/RHSA-2017:2553
- https://access.redhat.com/errata/RHSA-2017:2648
- https://access.redhat.com/errata/RHSA-2017:2665
- https://access.redhat.com/errata/RHSA-2017:2692
- https://access.redhat.com/errata/RHSA-2017:2698
- https://access.redhat.com/errata/RHSA-2017:2727
- https://mail.openvswitch.org/pipermail/ovs-dev/2017-May/332966.html
