# [H] CVE-2023-39191

## Summary
Severity: High
Advisory: CVE-2023-39191
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-10-04
Source: https://osv.dev/vulnerability/CVE-2023-39191
Type: osv

## Details
An improper input validation flaw was found in the eBPF subsystem in the Linux kernel. The issue occurs due to a lack of proper validation of dynamic pointers within user-supplied eBPF programs prior to executing them. This may allow an attacker with CAP_BPF privileges to escalate privileges and execute arbitrary code in the context of the kernel.

## References
- https://access.redhat.com/errata/RHSA-2024:0381
- https://access.redhat.com/errata/RHSA-2024:0439
- https://access.redhat.com/errata/RHSA-2024:0448
- https://access.redhat.com/security/cve/CVE-2023-39191
- https://access.redhat.com/errata/RHSA-2023:6583
- https://bugzilla.redhat.com/show_bug.cgi?id=2226783
- https://www.zerodayinitiative.com/advisories/ZDI-CAN-19399/
