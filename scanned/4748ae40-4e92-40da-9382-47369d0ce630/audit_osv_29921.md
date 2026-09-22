# [H] bpf, lsm: Add check for BPF LSM return value

## Summary
Severity: High
Advisory: CVE-2024-47703
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47703
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, lsm: Add check for BPF LSM return value

A bpf prog returning a positive number attached to file_alloc_security
hook makes kernel panic.

This happens because file system can not filter out the positive number
returned by the LSM prog using IS_ERR, and misinterprets this positive
number as a file pointer.

Given that hook file_alloc_security never returned positive number
before the introduction of BPF LSM, and other BPF LSM hooks may
encounter similar issues, this patch adds LSM return value check
in verifier, to ensure no unexpected value is returned.

## References
- https://git.kernel.org/stable/c/1050727d83e70449991c29dd1cf29fe936a63da3
- https://git.kernel.org/stable/c/27ca3e20fe80be85a92b10064dfeb56cb2564b1c
- https://git.kernel.org/stable/c/5d99e198be279045e6ecefe220f5c52f8ce9bfd5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47703.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47703
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
