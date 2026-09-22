# [M] CVE-2021-47426

## Summary
Severity: Medium
Advisory: CVE-2021-47426
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47426
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, s390: Fix potential memory leak about jit_data

Make sure to free jit_data through kfree() in the error path.

## References
- https://git.kernel.org/stable/c/686cb8b9f6b46787f035afe8fbd132a74e6b1bdd
- https://git.kernel.org/stable/c/a326f9c01cfbee4450ae49ce618ae6cbc0f76842
- https://git.kernel.org/stable/c/d590a410e472417a22336c7c37685bfb38e801f2
- https://git.kernel.org/stable/c/29fdb11ca88d3c490a3d56f0dc77eb9444d086be
