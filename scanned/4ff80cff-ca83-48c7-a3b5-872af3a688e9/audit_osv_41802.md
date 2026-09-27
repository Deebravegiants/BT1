# [H] ksmbd: OOB read regression in smb_check_perm_dacl() ACE-walk loops

## Summary
Severity: High
Advisory: CVE-2026-63909
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63909
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.140 <6.6.143, >=6.12.84 <6.12.93, >=6.18.25 <6.18.35, >=7.0.2 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: OOB read regression in smb_check_perm_dacl() ACE-walk loops

Commit d07b26f39246 ("ksmbd: require minimum ACE size in
smb_check_perm_dacl()") introduced a transposed bounds check:

    if (offsetof(struct smb_ace, sid) + aces_size < CIFS_SID_BASE_SIZE)

Since offsetof(..sid) is 8 and CIFS_SID_BASE_SIZE is 8, this evaluates
to `aces_size < 0`. Because `aces_size` is always non-negative, this
check becomes dead code and never breaks the loop.

Worse, that commit removed the old 4-byte guard, meaning the loop now
reads `ace->size` (offset 2) even when `aces_size` is 0-3 bytes. This
re-opens a 2-byte heap out-of-bounds (OOB) read past the pntsd allocation
during subsequent SMB2_CREATE operations.

Fix this by properly transposing the comparison to require at least
16 bytes (8-byte offset + 8-byte SID base), matching the correct form
used in smb_inherit_dacl().

## References
- https://git.kernel.org/stable/c/0e60dafe97eca61721f3db456f97d97a80c6c8ae
- https://git.kernel.org/stable/c/0fe08c5776a798f46df1fd74b331be26bdd644d6
- https://git.kernel.org/stable/c/4f7c131d2bdd7cd64b96f60d10be5ea72253f520
- https://git.kernel.org/stable/c/5500ba1d410aed1eded3eb04a76b10cfb4409334
- https://git.kernel.org/stable/c/94215d55b09445993929f4fc966061d61de74929
- https://git.kernel.org/stable/c/d333af32e4451285e427f2d9c29de3a39f6f6d48
- https://git.kernel.org/stable/c/f6324b4240cf0b26a84c33f68a1222d727ff4af2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63909.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63909
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
