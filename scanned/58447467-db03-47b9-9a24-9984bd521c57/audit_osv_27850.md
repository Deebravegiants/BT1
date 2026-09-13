# [H] mm: huge_memory: don't force huge page alignment on 32 bit

## Summary
Severity: High
Advisory: CVE-2024-26621
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2024-26621
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.81, >=6.2.0 <6.6.46, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: huge_memory: don't force huge page alignment on 32 bit

commit efa7df3e3bb5 ("mm: align larger anonymous mappings on THP
boundaries") caused two issues [1] [2] reported on 32 bit system or compat
userspace.

It doesn't make too much sense to force huge page alignment on 32 bit
system due to the constrained virtual address space.

[1] https://lore.kernel.org/linux-mm/d0a136a0-4a31-46bc-adf4-2db109a61672@kernel.org/
[2] https://lore.kernel.org/linux-mm/CAJuCfpHXLdQy1a2B6xN2d7quTYwg2OoZseYPZTRpU0eHHKD-sQ@mail.gmail.com/

## References
- http://www.openwall.com/lists/oss-security/2024/07/08/3
- http://www.openwall.com/lists/oss-security/2024/07/08/4
- http://www.openwall.com/lists/oss-security/2024/07/08/5
- http://www.openwall.com/lists/oss-security/2024/07/08/6
- http://www.openwall.com/lists/oss-security/2024/07/08/7
- http://www.openwall.com/lists/oss-security/2024/07/08/8
- http://www.openwall.com/lists/oss-security/2024/07/09/1
- http://www.openwall.com/lists/oss-security/2024/07/10/5
- http://www.openwall.com/lists/oss-security/2024/07/10/7
- http://www.openwall.com/lists/oss-security/2024/07/10/8
- http://www.openwall.com/lists/oss-security/2024/07/11/4
- http://www.openwall.com/lists/oss-security/2024/07/11/5
- http://www.openwall.com/lists/oss-security/2024/07/11/7
- http://www.openwall.com/lists/oss-security/2024/07/12/3
- http://www.openwall.com/lists/oss-security/2024/07/13/2
- http://www.openwall.com/lists/oss-security/2024/07/13/7
- http://www.openwall.com/lists/oss-security/2024/07/15/1
- http://www.openwall.com/lists/oss-security/2024/07/15/2
- http://www.openwall.com/lists/oss-security/2024/07/16/1
- http://www.openwall.com/lists/oss-security/2024/07/16/2
