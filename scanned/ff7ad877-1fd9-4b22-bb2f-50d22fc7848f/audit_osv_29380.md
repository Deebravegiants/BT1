# [H] net: dsa: mv88e6xxx: Correct check for empty list

## Summary
Severity: High
Advisory: CVE-2024-42224
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42224
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <4.19.318, >=4.20.0 <5.4.280, >=5.5.0 <5.10.222, >=5.11.0 <5.15.163, >=5.16.0 <6.1.98, >=6.2.0 <6.6.39, >=6.7.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: mv88e6xxx: Correct check for empty list

Since commit a3c53be55c95 ("net: dsa: mv88e6xxx: Support multiple MDIO
busses") mv88e6xxx_default_mdio_bus() has checked that the
return value of list_first_entry() is non-NULL.

This appears to be intended to guard against the list chip->mdios being
empty.  However, it is not the correct check as the implementation of
list_first_entry is not designed to return NULL for empty lists.

Instead, use list_first_entry_or_null() which does return NULL if the
list is empty.

Flagged by Smatch.
Compile tested only.

## References
- https://git.kernel.org/stable/c/2a2fe25a103cef73cde356e6d09da10f607e93f5
- https://git.kernel.org/stable/c/3bf8d70e1455f87856640c3433b3660a31001618
- https://git.kernel.org/stable/c/3f25b5f1635449036692a44b771f39f772190c1d
- https://git.kernel.org/stable/c/47d28dde172696031c880c5778633cdca30394ee
- https://git.kernel.org/stable/c/4c7f3950a9fd53a62b156c0fe7c3a2c43b0ba19b
- https://git.kernel.org/stable/c/8c2c3cca816d074c75a2801d1ca0dea7b0148114
- https://git.kernel.org/stable/c/aa03f591ef31ba603a4a99d05d25a0f21ab1cd89
- https://git.kernel.org/stable/c/f75625db838ade28f032dacd0f0c8baca42ecde4
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42224.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42224
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
