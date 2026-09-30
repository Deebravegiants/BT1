# [M] objtool: Fix memory leak in create_static_call_sections()

## Summary
Severity: Medium
Advisory: CVE-2023-53423
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53423
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.173, >=5.11.0 <5.15.100, >=5.16.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

objtool: Fix memory leak in create_static_call_sections()

strdup() allocates memory for key_name. We need to release the memory in
the following error paths. Add free() to avoid memory leak.

## References
- https://git.kernel.org/stable/c/3a75866a5ceff5d4fdd5471e06c4c4d03e0298b3
- https://git.kernel.org/stable/c/3da73f102309fe29150e5c35acd20dd82063ff67
- https://git.kernel.org/stable/c/a1368eaea058e451d20ea99ca27e72d9df0d16dd
- https://git.kernel.org/stable/c/a8f63d747bf7c983882a5ea7456a5f84ad3acad5
- https://git.kernel.org/stable/c/d131718d9c45d559951f57c4b88209ca407433c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53423.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53423
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
