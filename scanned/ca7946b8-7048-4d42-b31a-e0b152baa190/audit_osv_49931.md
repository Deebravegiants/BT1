# [M] CVE-2019-3887

## Summary
Severity: Medium
Advisory: CVE-2019-3887
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2019-04-09
Source: https://osv.dev/vulnerability/CVE-2019-3887
Type: osv

## Details
A flaw was found in the way KVM hypervisor handled x2APIC Machine Specific Rregister (MSR) access with nested(=1) virtualization enabled. In that, L1 guest could access L0's APIC register values via L2 guest, when 'virtualize x2APIC mode' is enabled. A guest could use this flaw to potentially crash the host kernel resulting in DoS issue. Kernel versions from 4.16 and newer are vulnerable to this issue.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IWPOIII2L73HV5PGXSGMRMKQIK47UIYE/
- https://usn.ubuntu.com/3979-1/
- https://usn.ubuntu.com/3980-1/
- https://usn.ubuntu.com/3980-2/
- http://www.securityfocus.com/bid/107850
- https://access.redhat.com/errata/RHSA-2019:2703
- https://access.redhat.com/errata/RHSA-2019:2741
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3887
