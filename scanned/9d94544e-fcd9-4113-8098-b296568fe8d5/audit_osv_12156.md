# [M] CVE-2018-1062

## Summary
Severity: Medium
Advisory: CVE-2018-1062
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-03-06
Source: https://osv.dev/vulnerability/CVE-2018-1062
Type: osv

## Details
A vulnerability was discovered in oVirt 4.1.x before 4.1.9, where the combination of Enable Discard and Wipe After Delete flags for VM disks managed by oVirt, could cause a disk to be incompletely zeroed when removed from a VM. If the same storage blocks happen to be later allocated to a new disk attached to another VM, potentially sensitive data could be revealed to privileged users of that VM.

## References
- http://www.securityfocus.com/bid/103433
- https://access.redhat.com/errata/RHBA-2018:0135
- https://gerrit.ovirt.org/#/c/84861/
- https://gerrit.ovirt.org/#/c/84875/
- https://bugzilla.redhat.com/show_bug.cgi?id=1549944
