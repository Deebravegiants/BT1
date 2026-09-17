# [H] CVE-2018-17205

## Summary
Severity: High
Advisory: CVE-2018-17205
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-19
Source: https://osv.dev/vulnerability/CVE-2018-17205
Type: osv

## Details
An issue was discovered in Open vSwitch (OvS) 2.7.x through 2.7.6, affecting ofproto_rule_insert__ in ofproto/ofproto.c. During bundle commit, flows that are added in a bundle are applied to ofproto in order. If a flow cannot be added (e.g., the flow action is a go-to for a group id that does not exist), OvS tries to revert back all previous flows that were successfully applied from the same bundle. This is possible since OvS maintains list of old flows that were replaced by flows from the bundle. While reinserting old flows, OvS has an assertion failure due to a check on rule state != RULE_INITIALIZED. This would work for new flows, but for an old flow the rule state is RULE_REMOVED. The assertion failure causes an OvS crash.

## References
- https://access.redhat.com/errata/RHSA-2018:3500
- https://access.redhat.com/errata/RHSA-2019:0053
- https://access.redhat.com/errata/RHSA-2019:0081
- https://usn.ubuntu.com/3873-1/
- https://github.com/openvswitch/ovs/commit/0befd1f3745055c32940f5faf9559be6a14395e6
