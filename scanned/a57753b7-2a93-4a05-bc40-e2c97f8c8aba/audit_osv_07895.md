# [H] URL file scheme drive letter buffer overflow

## Summary
Severity: High
Advisory: CURL-CVE-2017-9502
Aliases: CVE-2017-9502
Published: 2017-06-14
Source: https://osv.dev/vulnerability/CURL-CVE-2017-9502
Type: osv

## Details
When libcurl is given either

 1. a file: URL that does not use two slashes following the colon, or
 2. is told that file is the default scheme to use for URLs without scheme

... and the given path starts with a drive letter and libcurl is built for
Windows or DOS, then libcurl would copy the path with a wrong offset, so that
the end of the given path would write beyond the malloc buffer. Up to seven
bytes too much.
