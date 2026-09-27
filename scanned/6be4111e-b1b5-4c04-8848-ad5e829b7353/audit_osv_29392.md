# [H] mm: huge_memory: use !CONFIG_64BIT to relax huge page alignment on 32 bit machines

## Summary
Severity: High
Advisory: CVE-2024-42258
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-08-12
Source: https://osv.dev/vulnerability/CVE-2024-42258
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.105, >=6.2.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: huge_memory: use !CONFIG_64BIT to relax huge page alignment on 32 bit machines

Yves-Alexis Perez reported commit 4ef9ad19e176 ("mm: huge_memory: don't
force huge page alignment on 32 bit") didn't work for x86_32 [1].  It is
because x86_32 uses CONFIG_X86_32 instead of CONFIG_32BIT.

!CONFIG_64BIT should cover all 32 bit machines.

[1] https://lore.kernel.org/linux-mm/CAHbLzkr1LwH3pcTgM+aGQ31ip2bKqiqEQ8=FQB+t2c3dhNKNHA@mail.gmail.com/

## References
- https://git.kernel.org/stable/c/7e1f4efb8d6140b2ec79bf760c43e1fc186e8dfc
- https://git.kernel.org/stable/c/89f2914dd4b47d2fad3deef0d700f9526d98d11f
- https://git.kernel.org/stable/c/a5c399fe433a115e9d3693169b5f357f3194af0a
- https://git.kernel.org/stable/c/d9592025000b3cf26c742f3505da7b83aedc26d5
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42258.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42258
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
