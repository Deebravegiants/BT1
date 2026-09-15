# [M] CVE-2021-47522

## Summary
Severity: Medium
Advisory: CVE-2021-47522
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47522
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: bigbenff: prevent null pointer dereference

When emulating the device through uhid, there is a chance we don't have
output reports and so report_field is null.

## References
- https://git.kernel.org/stable/c/58f15f5ae7786c824868f3a7e093859b74669ce7
- https://git.kernel.org/stable/c/6272b17001e6fdcf7b4a16206287010a1523fa6e
- https://git.kernel.org/stable/c/8e0ceff632f48175ec7fb4706129c55ca8a7c7bd
- https://git.kernel.org/stable/c/918aa1ef104d286d16b9e7ef139a463ac7a296f0
