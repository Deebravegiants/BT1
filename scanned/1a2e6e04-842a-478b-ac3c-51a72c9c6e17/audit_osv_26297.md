# [H] wifi: wilc1000: use vmm_table as array in wilc struct

## Summary
Severity: High
Advisory: CVE-2023-52768
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52768
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.140, >=5.16.0 <6.1.64, >=6.0.0 <6.5.13, >=6.2.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: wilc1000: use vmm_table as array in wilc struct

Enabling KASAN and running some iperf tests raises some memory issues with
vmm_table:

BUG: KASAN: slab-out-of-bounds in wilc_wlan_handle_txq+0x6ac/0xdb4
Write of size 4 at addr c3a61540 by task wlan0-tx/95

KASAN detects that we are writing data beyond range allocated to vmm_table.
There is indeed a mismatch between the size passed to allocator in
wilc_wlan_init, and the range of possible indexes used later: allocation
size is missing a multiplication by sizeof(u32)

## References
- https://git.kernel.org/stable/c/05ac1a198a63ad66bf5ae8b7321407c102d40ef3
- https://git.kernel.org/stable/c/3ce1c2c3999b232258f7aabab311d47dda75605c
- https://git.kernel.org/stable/c/4b0d6ddb6466d10df878a7787f175a0e4adc3e27
- https://git.kernel.org/stable/c/541b3757fd443a68ed8d25968eae511a8275e7c8
- https://git.kernel.org/stable/c/6aaf7cd8bdfe245d3c9a8b48fe70c2011965948e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52768.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52768
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
