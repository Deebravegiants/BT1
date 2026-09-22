# [H] SSL out of buffer access

## Summary
Severity: High
Advisory: CURL-CVE-2017-8818
Aliases: CVE-2017-8818
Published: 2017-11-29
Source: https://osv.dev/vulnerability/CURL-CVE-2017-8818
Type: osv

## Details
libcurl contains an out boundary access flaw in SSL related code.

When allocating memory for a connection (the internal struct called
`connectdata`), a certain amount of memory is allocated at the end of the
struct to be used for SSL related structs. Those structs are used by the
particular SSL library libcurl is built to use. The application can also tell
libcurl which specific SSL library to use if it was built to support more than
one.

The math used to calculate the extra memory amount necessary for the SSL
library was wrong on 32-bit systems, which made the allocated memory too small
by 4 bytes. The last struct member of the last object within the memory area
could then be outside of what was allocated. Accessing that member could lead
to a crash or other undefined behaviors depending on what memory that is
present there and how the particular SSL library decides to act on that memory
content.

Specifically the vulnerability is present if libcurl was built so that
`sizeof(long long *) < sizeof(long long)` which as far as we are aware only
happens in 32-bit builds.
