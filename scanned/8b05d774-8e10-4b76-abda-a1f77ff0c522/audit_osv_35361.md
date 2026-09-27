# [H] dm-verity: disable recursive forward error correction

## Summary
Severity: High
Advisory: CVE-2025-71161
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2025-71161
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.15.209, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm-verity: disable recursive forward error correction

There are two problems with the recursive correction:

1. It may cause denial-of-service. In fec_read_bufs, there is a loop that
has 253 iterations. For each iteration, we may call verity_hash_for_block
recursively. There is a limit of 4 nested recursions - that means that
there may be at most 253^4 (4 billion) iterations. Red Hat QE team
actually created an image that pushes dm-verity to this limit - and this
image just makes the udev-worker process get stuck in the 'D' state.

2. It doesn't work. In fec_read_bufs we store data into the variable
"fio->bufs", but fio bufs is shared between recursive invocations, if
"verity_hash_for_block" invoked correction recursively, it would
overwrite partially filled fio->bufs.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/232948cf600fba69aff36b25d85ef91a73a35756
- https://git.kernel.org/stable/c/4220cb37406915c926c0e4a3dbab77cd9cceeb1e
- https://git.kernel.org/stable/c/897d9006e75f46f8bd7df78faa424327ae6a4bcf
- https://git.kernel.org/stable/c/8b821ca892cfeeaf0bedc9fc72717294f67144d5
- https://git.kernel.org/stable/c/d9f3e47d3fae0c101d9094bc956ed24e7a0ee801
- https://git.kernel.org/stable/c/e227d2b229c7529bd98d348efc55262ccf24ab35
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71161.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71161
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
