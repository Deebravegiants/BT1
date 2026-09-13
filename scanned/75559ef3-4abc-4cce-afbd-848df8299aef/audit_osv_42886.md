# [H] dm-log: fix a bitset_size overflow on 32bit machines

## Summary
Severity: High
Advisory: CVE-2026-72105
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72105
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm-log: fix a bitset_size overflow on 32bit machines

Commit c20e36b7631d ("dm log: fix out-of-bounds write due to
region_count overflow") made sure that region_count could fit in an
unsigned int. But the bitmap memory isn't allocated based on
region_count. It uses bitset_size (a size_t variable). The first step of
calculating bitset_size is to set it to region_count, rounded up to a
multiple of BITS_PER_LONG. If region_size is less than BITS_PER_LONG
smaller than UINT_MAX, it will get rounded up to 2^32. On a 32bit
architecture, this will make bitset_size wrap around to 0 and fail,
despite region_count being valid.

Since bitset_size gets divided by 8, it can hold any valid region_count.
It just needs a special case to handle the rollover. If it is 0, the
value rolled over, and bitset size should be set to the number of bytes
needed to hold 2^32 bits.

## References
- https://git.kernel.org/stable/c/1c3412b584e1fb6c665ff33ba7259253bc0082cb
- https://git.kernel.org/stable/c/4b0de5a3ac1fd42acb0dc1f80ac5747e3287d723
- https://git.kernel.org/stable/c/567602fa72d57169365cbc589e0b8c3be900636d
- https://git.kernel.org/stable/c/79feb87ab2396d49b9b65e4bb815d33cc71cba47
- https://git.kernel.org/stable/c/9743132a41f4d9d0e54c5f2adcb821b04796bab1
- https://git.kernel.org/stable/c/cdc4ddf9db2cb79f4ab86b1a509b7ac21b0b6cf5
- https://git.kernel.org/stable/c/d05e0edfecf5260e6dddd28b2f0cce02bfc6ed7a
- https://git.kernel.org/stable/c/e0b0163a65758ec3a2361ae1cea407898c27f21e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72105.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72105
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
