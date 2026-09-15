# [M] CVE-2022-3344

## Summary
Severity: Medium
Advisory: CVE-2022-3344
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-25
Source: https://osv.dev/vulnerability/CVE-2022-3344
Type: osv

## Details
A flaw was found in the KVM's AMD nested virtualization (SVM). A malicious L1 guest could purposely fail to intercept the shutdown of a cooperative nested guest (L2), possibly leading to a page fault and kernel panic in the host (L0).

## References
- https://lore.kernel.org/lkml/20221020093055.224317-5-mlevitsk%40redhat.com/T/
- https://bugzilla.redhat.com/show_bug.cgi?id=2130278
