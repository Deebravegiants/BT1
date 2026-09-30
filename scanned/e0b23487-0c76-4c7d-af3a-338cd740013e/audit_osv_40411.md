# [H] iomap: avoid potential null folio->mapping deref during error reporting

## Summary
Severity: High
Advisory: CVE-2026-53165
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53165
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

iomap: avoid potential null folio->mapping deref during error reporting

When a buffered read fails, iomap_finish_folio_read() reports the error
with fserror_report_io(folio->mapping->host, ...). This is called after
ifs->read_bytes_pending has been decremented by the bytes attempted to
be read.

For a folio split across multiple read completions, the folio is only
guaranteed to stay locked while read_bytes_pending > 0. Once
iomap_finish_folio_read() decrements read_bytes_pending, another
in-flight read can complete and end the read on the folio, which unlocks
it. This allows truncate logic to run and detach the folio (set
folio->mapping to NULL). The error reporting path then can dereference a
NULL folio->mapping. As reported by Sam Sun, this is the race that can
occur:

CPU0: failed completion      CPU1: final completion     CPU2: truncate
-----------------------      ----------------------     --------------
read_bytes_pending -= len
finished = false
/* preempted before
   fserror_report_io() */
			     read_bytes_pending -= len
			     finished = true
			     folio_end_read()
							truncate clears
							folio->mapping
fserror_report_io(
  folio->mapping->host, ...)
	      ^ NULL deref

Fix this by reporting the error first before decrementing
ifs->read_bytes_pending.

## References
- https://git.kernel.org/stable/c/1ad453817a4077230d1ba88eb0868f05f824449a
- https://git.kernel.org/stable/c/2eea7f44b9c8b42fd7d3a1a87c06a7cd1b99c327
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53165.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53165
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
