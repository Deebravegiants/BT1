# [H] netfs: Fix write streaming disablement if fd open O_RDWR

## Summary
Severity: High
Advisory: CVE-2026-64158
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64158
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix write streaming disablement if fd open O_RDWR

In netfs_perform_write(), "write streaming" (the caching of dirty data in
dirty but !uptodate folios) is performed to avoid the need to read data
that is just going to get immediately overwritten.  However, this is/will
be disabled in three circumstances: if the fd is open O_RDWR, if fscache is
in use (as we need to round out the blocks for DIO) or if content
encryption is enabled (again for rounding out purposes).

The idea behind disabling it if the fd is open O_RDWR is that we'd need to
flush the write-streaming page before we could read the data, particularly
through mmap.  But netfs now fills in the gaps if ->read_folio() is called
on the page, so that is unnecessary.  Further, this doesn't actually work
if a separate fd is open for reading.

Fix this by removing the check for O_RDWR, thereby allowing streaming
writes even when we might read.

This caused a number of problems with the generic/522 xfstest, but those
are now fixed.

## References
- https://git.kernel.org/stable/c/616578e40dcba3f94810d841c5a52b7e3bc8ede7
- https://git.kernel.org/stable/c/70a7b9193bbbfceaab5974de66834c64ccc875dd
- https://git.kernel.org/stable/c/7a9fa5b020a3a40f8291a71cd44c08d931da430d
- https://git.kernel.org/stable/c/9adf8e47d73d5e3c2fe77dea649dcde350ccd65c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64158.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64158
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
