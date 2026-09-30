# [H] io_uring/net: ensure vectored buffer node import is tied to notification

## Summary
Severity: High
Advisory: CVE-2025-68294
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68294
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.17.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/net: ensure vectored buffer node import is tied to notification

When support for vectored registered buffers was added, the import
itself is using 'req' rather than the notification io_kiocb, sr->notif.
For non-vectored imports, sr->notif is correctly used. This is important
as the lifetime of the two may be different. Use the correct io_kiocb
for the vectored buffer import.

## References
- https://git.kernel.org/stable/c/14459281e027f23b70885c1cc1032a71c0efd8d7
- https://git.kernel.org/stable/c/f6041803a831266a2a5a5b5af66f7de0845bcbf3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68294.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68294
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
