# [H] x86/MCE/AMD: Use an u64 for bank_map

## Summary
Severity: High
Advisory: CVE-2023-53474
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53474
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/MCE/AMD: Use an u64 for bank_map

Thee maximum number of MCA banks is 64 (MAX_NR_BANKS), see

  a0bc32b3cacf ("x86/mce: Increase maximum number of banks to 64").

However, the bank_map which contains a bitfield of which banks to
initialize is of type unsigned int and that overflows when those bit
numbers are >= 32, leading to UBSAN complaining correctly:

  UBSAN: shift-out-of-bounds in arch/x86/kernel/cpu/mce/amd.c:1365:38
  shift exponent 32 is too large for 32-bit type 'int'

Change the bank_map to a u64 and use the proper BIT_ULL() macro when
modifying bits in there.

  [ bp: Rewrite commit message. ]

## References
- https://git.kernel.org/stable/c/11c58a0c1937c157dbdf82d5ab634d68c99f3098
- https://git.kernel.org/stable/c/4c1cdec319b9aadb65737c3eb1f5cb74bd6aa156
- https://git.kernel.org/stable/c/67bb7521b6420d81dab7538c0686f18f7d6d09f4
- https://git.kernel.org/stable/c/9669fa17287c3af2bbd4868d4c8fdd9e57f8332e
- https://git.kernel.org/stable/c/a9b9ea0e63a0ec5e97bf1219ab6dcbd55e362f83
- https://git.kernel.org/stable/c/ba8ffb1251eb629c2ec35220e3896cf4f7b888a7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53474.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53474
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
