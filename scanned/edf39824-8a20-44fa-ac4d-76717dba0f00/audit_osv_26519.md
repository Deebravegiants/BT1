# [M] wifi: iwl4965: Add missing check for create_singlethread_workqueue()

## Summary
Severity: Medium
Advisory: CVE-2023-53302
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53302
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwl4965: Add missing check for create_singlethread_workqueue()

Add the check for the return value of the create_singlethread_workqueue()
in order to avoid NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/26e6775f75517ad6844fe5b79bc5f3fa8c22ee61
- https://git.kernel.org/stable/c/2f85c768bea2057e3299d19514da9e932c4f92d2
- https://git.kernel.org/stable/c/3185d6cfc59277a77bf311dce701b7e25193f66a
- https://git.kernel.org/stable/c/874a85051cc8df8c5b928d8ff172b342cdc5424b
- https://git.kernel.org/stable/c/878a7c8357764e08bc778bcb26127fc12a4b36b7
- https://git.kernel.org/stable/c/c002d2741400771171b68dde9af937a4dfa0d1b3
- https://git.kernel.org/stable/c/f15ef0ebcf56be1d4a3c9a7a80a1f1f82ab0eaad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53302.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53302
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
