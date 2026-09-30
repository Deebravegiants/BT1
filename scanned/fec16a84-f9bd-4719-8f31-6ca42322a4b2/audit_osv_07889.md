# [M] IMAP FETCH response out of bounds read

## Summary
Severity: Medium
Advisory: CURL-CVE-2017-1000257
Aliases: CVE-2017-1000257
Published: 2017-10-23
Source: https://osv.dev/vulnerability/CURL-CVE-2017-1000257
Type: osv

## Details
libcurl contains a buffer overrun flaw in the IMAP handler.

An IMAP FETCH response line indicates the size of the returned data, in number
of bytes. When that response says the data is zero bytes, libcurl would pass
on that (non-existing) data with a pointer and the size (zero) to the
deliver-data function.

libcurl's deliver-data function treats zero as a magic number and invokes
strlen() on the data to figure out the length. The strlen() is called on a
heap based buffer that might not be null-terminated so libcurl might read
beyond the end of it into whatever memory lies after (or crash) and then
deliver that to the application as if it was actually downloaded.
