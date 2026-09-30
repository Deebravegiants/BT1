# [H] ksmbd: validate ACE size against SID sub-authorities

## Summary
Severity: High
Advisory: CVE-2026-68097
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68097
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate ACE size against SID sub-authorities

set_ntacl_dacl() validates sid.num_subauth before copying an ACE, but
does not verify that the declared ACE size contains all sub-authorities
described by that field. An undersized ACE can therefore be copied
and later make the POSIX ACL deduplication walk inspect data beyond
the copied ACE boundary.

The existing initial bound check is also too small. It only ensures
that the ACE size field is accessible before set_ntacl_dacl() reads
sid.num_subauth farther into the input buffer.

Require enough input for the fixed SID header before accessing
num_subauth, reject ACEs smaller than that header, and skip ACEs
whose declared size cannot contain the complete SID. This makes the
validation consistent with the other ACE walk paths.

## References
- https://git.kernel.org/stable/c/337022d9dfac441c3b35e4455a51aa981996e02e
- https://git.kernel.org/stable/c/5152c6d49e3fd4e9f2e857c57527aead752f1f87
- https://git.kernel.org/stable/c/61fd3559199f7fa693dcbff35e59477e24af041a
- https://git.kernel.org/stable/c/62d80d7c2d9428085e7458ad4c06ca8c0984039b
- https://git.kernel.org/stable/c/b7cb5bf0855470799f12da825de91e48951b3876
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68097.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68097
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
