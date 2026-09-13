# [M] CVE-2017-14970

## Summary
Severity: Medium
Advisory: CVE-2017-14970
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-02
Source: https://osv.dev/vulnerability/CVE-2017-14970
Type: osv

## Details
In lib/ofp-util.c in Open vSwitch (OvS) before 2.8.1, there are multiple memory leaks while parsing malformed OpenFlow group mod messages. NOTE: the vendor disputes the relevance of this report, stating "it can only be triggered by an OpenFlow controller, but OpenFlow controllers have much more direct and powerful ways to force Open vSwitch to allocate memory, such as by inserting flows into the flow table."

## References
- https://mail.openvswitch.org/pipermail/ovs-dev/2017-September/339085.html
- https://mail.openvswitch.org/pipermail/ovs-dev/2017-September/339086.html
