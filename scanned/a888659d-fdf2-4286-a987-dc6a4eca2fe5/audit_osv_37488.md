# [C] ksmbd: fix out-of-bounds write in smb2_get_ea() EA alignment

## Summary
Severity: Critical
Advisory: CVE-2026-31705
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31705
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.175, >=6.2.0 <6.6.136, >=6.6.0 <6.12.84, >=6.7.0 <6.18.25, >=6.13.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix out-of-bounds write in smb2_get_ea() EA alignment

smb2_get_ea() applies 4-byte alignment padding via memset() after
writing each EA entry. The bounds check on buf_free_len is performed
before the value memcpy, but the alignment memset fires unconditionally
afterward with no check on remaining space.

When the EA value exactly fills the remaining buffer (buf_free_len == 0
after value subtraction), the alignment memset writes 1-3 NUL bytes
past the buf_free_len boundary. In compound requests where the response
buffer is shared across commands, the first command (e.g., READ) can
consume most of the buffer, leaving a tight remainder for the QUERY_INFO
EA response. The alignment memset then overwrites past the physical
kvmalloc allocation into adjacent kernel heap memory.

Add a bounds check before the alignment memset to ensure buf_free_len
can accommodate the padding bytes.

This is the same bug pattern fixed by commit beef2634f81f ("ksmbd: fix
potencial OOB in get_file_all_info() for compound requests") and
commit fda9522ed6af ("ksmbd: fix OOB write in QUERY_INFO for compound
requests"), both of which added bounds checks before unconditional
writes in QUERY_INFO response handlers.

## References
- https://git.kernel.org/stable/c/30010c952077a1c89ecdd71fc4d574c75a8f5617
- https://git.kernel.org/stable/c/790304c02bf9bd7b8171feda4294d6e62d32ae8f
- https://git.kernel.org/stable/c/922d48fe8c19f388ffa2f709f33acaae4e408de2
- https://git.kernel.org/stable/c/98f3de6ef4efbd899348d333f0902dc4ff14380c
- https://git.kernel.org/stable/c/ddbbc8b2a09dd2cfed90871313e3691ae1db08a2
- https://git.kernel.org/stable/c/ffbce350c6fd1e99116ea57383b9031717e36d3b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31705.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31705
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
