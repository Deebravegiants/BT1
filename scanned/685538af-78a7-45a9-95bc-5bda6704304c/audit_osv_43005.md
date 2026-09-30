# [H] smb: client: fix overflow in passthrough ioctl bounds check

## Summary
Severity: High
Advisory: CVE-2026-72310
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72310
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix overflow in passthrough ioctl bounds check

smb2_ioctl_query_info() validates the PASSTHRU_FSCTL response payload
before copying it to userspace.

The payload offset and length both come from 32-bit fields. The bounds
check currently adds OutputOffset and qi.input_buffer_length directly, so
the addition can wrap in 32-bit arithmetic before the result is compared
against the response buffer length.

A malicious server can use a large OutputOffset and a small OutputCount
to make the wrapped sum pass the bounds check. The later copy_to_user()
then reads from io_rsp + OutputOffset, outside the response buffer.

Use size_add() for the offset plus length check so overflow is treated as
out of bounds.

## References
- https://git.kernel.org/stable/c/160045fc943f6c46b227644261252c8a22b8a87a
- https://git.kernel.org/stable/c/1627e7d5c9b09721a141d07cedb178882f1ded67
- https://git.kernel.org/stable/c/175357ee0c596cb82054650dfa32fda51ad35aaa
- https://git.kernel.org/stable/c/1a638c55f2db6cb2296e5e3138015dd8fd9d4aa9
- https://git.kernel.org/stable/c/63feb687e89a3a52a31e6e01764117cc500f1974
- https://git.kernel.org/stable/c/a4f27ad055392fa164f5649e89a3637b033c5fcc
- https://git.kernel.org/stable/c/b30771b69eafae750afb7385fbcc3d77ed3f3670
- https://git.kernel.org/stable/c/dbd126539c098dba3159ce7d34b10b2daddcbd0f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72310.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72310
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
