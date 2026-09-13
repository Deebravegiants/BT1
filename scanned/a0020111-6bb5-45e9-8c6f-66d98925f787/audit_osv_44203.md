# [H] s390/qeth: validate user buffer length in SNMP and ARP query ioctls

## Summary
Severity: High
Advisory: CVE-2026-80584
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80584
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/qeth: validate user buffer length in SNMP and ARP query ioctls

qeth_snmp_command() and qeth_l3_arp_query() allocate a buffer sized by
a user-supplied length (udata_len) without checking a lower bound, then
set udata_offset to a fixed non-zero value and pass both to a reply
callback. The callback bounds-checks the copy with

        if ((udata_len - udata_offset) < len)

Both fields are u32, so a udata_len smaller than udata_offset makes the
subtraction wrap and the check pass, and the following memcpy() writes
past the allocation. A udata_len of 0 also yields ZERO_SIZE_PTR from
kzalloc(), which the existing NULL check does not catch.

Reject buffers smaller than udata_offset before allocating, so the
callback subtraction can no longer underflow.

## References
- https://git.kernel.org/stable/c/3083818e67bcd656965797fbac9a3d6c1d44f78a
- https://git.kernel.org/stable/c/46443eaddebd84c51940857b11787229be169dec
- https://git.kernel.org/stable/c/75fb3151513d7d9f77a8f9545418279b119c06b8
- https://git.kernel.org/stable/c/91935843f9396a9e45253e2c0d4337ca1371754b
- https://git.kernel.org/stable/c/9d00eeb2d27f4cc817c5e408760226d43f811ec6
- https://git.kernel.org/stable/c/a3083647747942ea32faf14560d6397ff3068046
- https://git.kernel.org/stable/c/cc423f4105fe145b33e1d7cad34245a798358f73
- https://git.kernel.org/stable/c/d141f087b1af656f055d7c5793a3e87817ba0bbe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80584.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80584
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
