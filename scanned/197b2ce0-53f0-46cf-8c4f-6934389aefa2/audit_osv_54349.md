# [M] CVE-2023-5090

## Summary
Severity: Medium
Advisory: CVE-2023-5090
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-06
Source: https://osv.dev/vulnerability/CVE-2023-5090
Type: osv

## Details
A flaw was found in KVM. An improper check in svm_set_x2apic_msr_interception() may allow direct access to host x2apic msrs when the guest resets its apic, potentially leading to a denial of service condition.

## References
- https://access.redhat.com/errata/RHSA-2024:2758
- https://access.redhat.com/errata/RHSA-2024:3854
- https://access.redhat.com/errata/RHSA-2024:3855
- https://access.redhat.com/errata/RHSA-2024:4211
- https://access.redhat.com/errata/RHSA-2024:4352
- https://access.redhat.com/security/cve/CVE-2023-5090
- https://bugzilla.redhat.com/show_bug.cgi?id=2248122
