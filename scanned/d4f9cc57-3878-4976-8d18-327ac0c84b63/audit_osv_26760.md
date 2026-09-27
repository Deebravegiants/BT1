# [H] crypto: lib/mpi - avoid null pointer deref in mpi_cmp_ui()

## Summary
Severity: High
Advisory: CVE-2023-53817
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53817
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <4.14.326, >=4.15.0 <4.19.295, >=4.20.0 <5.4.257, >=5.5.0 <5.10.197, >=5.11.0 <5.15.133, >=5.16.0 <6.1.55, >=6.2.0 <6.5.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: lib/mpi - avoid null pointer deref in mpi_cmp_ui()

During NVMeTCP Authentication a controller can trigger a kernel
oops by specifying the 8192 bit Diffie Hellman group and passing
a correctly sized, but zeroed Diffie Hellamn value.
mpi_cmp_ui() was detecting this if the second parameter was 0,
but 1 is passed from dh_is_pubkey_valid(). This causes the null
pointer u->d to be dereferenced towards the end of mpi_cmp_ui()

## References
- https://git.kernel.org/stable/c/0fc7147c694394f8a8cbc19570c6bc918cac0906
- https://git.kernel.org/stable/c/12ac013ad7ff0df066451e825801d805095b3776
- https://git.kernel.org/stable/c/61f5453e9706e99713825594e0c8f9031485fb5f
- https://git.kernel.org/stable/c/67589d247909043e94d2dd5fb590958e0f99d58d
- https://git.kernel.org/stable/c/9e47a758b70167c9301d2b44d2569f86c7796f2d
- https://git.kernel.org/stable/c/ae63e84ffda74267bf7277c38415ba38389229a0
- https://git.kernel.org/stable/c/d3ad023a39f1127dcfd331c562673355dc078650
- https://git.kernel.org/stable/c/fde791e8a96a64ea7b0ad2440e43586447a209c6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53817.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53817
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
