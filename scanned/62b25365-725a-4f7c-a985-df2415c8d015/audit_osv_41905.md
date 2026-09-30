# [H] fs/statmount: fix slab out-of-bounds write in statmount_mnt_idmap

## Summary
Severity: High
Advisory: CVE-2026-64074
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64074
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/statmount: fix slab out-of-bounds write in statmount_mnt_idmap

statmount_mnt_idmap() writes one mapping with seq_printf() and then
manually advances seq->count to include the NUL separator.

If seq_printf() overflows, seq_set_overflow() sets seq->count to
seq->size. The manual seq->count++ changes this to seq->size + 1.
seq_has_overflowed() then no longer detects the overflow. The corrupted
count returns to statmount_string(), which later executes:

    seq->buf[seq->count++] = '\0';

This causes a 1-byte NULL out-of-bounds write on the dynamically
allocated seq buffer.

Fix this by checking for overflow immediately after seq_printf().

## References
- https://git.kernel.org/stable/c/93614949dc86f068e3c32c32cf1ee2a2323177a7
- https://git.kernel.org/stable/c/a3bf0f28d4ba16e1f35f8c983bb04426b87e2a78
- https://git.kernel.org/stable/c/e37ea2c6f17f273813ea4e8e94c102591d598ce1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64074.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64074
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
