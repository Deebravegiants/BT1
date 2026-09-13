# [H] isofs: bound Rock Ridge symlink components to the SL record

## Summary
Severity: High
Advisory: CVE-2026-64317
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64317
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

isofs: bound Rock Ridge symlink components to the SL record

get_symlink_chunk() and the SL handling in
parse_rock_ridge_inode_internal() walk the variable-length components of
a Rock Ridge "SL" (symbolic link) record.  Each component is a two-byte
header (flags, len) followed by len bytes of text, so it occupies
slp->len + 2 bytes.  Both loops read slp->len and advance to the next
component, and get_symlink_chunk() additionally does
memcpy(rpnt, slp->text, slp->len), but neither checks that the component
lies within the SL record before dereferencing it.

A crafted SL record whose component declares a len that runs past the
record (rr->len) therefore triggers an out-of-bounds read of up to 255
bytes.  When the record sits at the tail of its backing buffer - for
example a small kmalloc()ed continuation block reached through a CE
record - the read crosses the allocation; get_symlink_chunk() then
copies the out-of-bounds bytes into the symlink body returned to user
space by readlink(), disclosing adjacent kernel memory.

ISO 9660 images are routinely mounted from untrusted removable media -
desktop environments auto-mount them (e.g. via udisks2) without
CAP_SYS_ADMIN - so the record contents are attacker-controlled.

Reject any component that does not fit in the remaining record bytes
before using it.  In get_symlink_chunk() return NULL, like the existing
output-buffer (plimit) checks, so a malformed record makes readlink()
fail with -EIO rather than silently returning a truncated target; in
parse_rock_ridge_inode_internal() stop the inode-size walk.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/1015e1c4b2fadd9c09704e24738e46598778c869
- https://git.kernel.org/stable/c/36fe7d25dbc40da0c6b1dd4513a4f69ac6164eee
- https://git.kernel.org/stable/c/5fa1d6a5ec2356d2107dead614437c66fa7138b1
- https://git.kernel.org/stable/c/6bf41db09ef935d76fcc84ccf213b42c18de95ee
- https://git.kernel.org/stable/c/9830725078c8483c6831ec10222ae724806ea36b
- https://git.kernel.org/stable/c/a22cb6bb54dc167047ea9e70d97dfbc2c15649e3
- https://git.kernel.org/stable/c/b5699642640d6cff357638738c5293985cd5a53d
- https://git.kernel.org/stable/c/b736b12108fd116c41777628f5a333791604df26
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64317.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64317
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
