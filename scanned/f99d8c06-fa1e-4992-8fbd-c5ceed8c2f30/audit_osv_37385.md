# [C] iomap: fix invalid folio access when i_blkbits differs from I/O granularity

## Summary
Severity: Critical
Advisory: CVE-2026-31463
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31463
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

iomap: fix invalid folio access when i_blkbits differs from I/O granularity

Commit aa35dd5cbc06 ("iomap: fix invalid folio access after
folio_end_read()") partially addressed invalid folio access for folios
without an ifs attached, but it did not handle the case where
1 << inode->i_blkbits matches the folio size but is different from the
granularity used for the IO, which means IO can be submitted for less
than the full folio for the !ifs case.

In this case, the condition:

  if (*bytes_submitted == folio_len)
    ctx->cur_folio = NULL;

in iomap_read_folio_iter() will not invalidate ctx->cur_folio, and
iomap_read_end() will still be called on the folio even though the IO
helper owns it and will finish the read on it.

Fix this by unconditionally invalidating ctx->cur_folio for the !ifs
case.

## References
- https://git.kernel.org/stable/c/4a927f670cdb0def226f9f85f42a9f19d9e09c88
- https://git.kernel.org/stable/c/bd71fb3fea9945987053968f028a948997cba8cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31463.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31463
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
