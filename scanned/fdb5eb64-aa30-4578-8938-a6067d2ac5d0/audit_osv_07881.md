# [M] printf floating point buffer overflow

## Summary
Severity: Medium
Advisory: CURL-CVE-2016-9586
Aliases: CVE-2016-9586
Published: 2016-12-21
Source: https://osv.dev/vulnerability/CURL-CVE-2016-9586
Type: osv

## Details
libcurl's implementation of the printf() functions triggers a buffer overflow
when doing a large floating point output. The bug occurs when the conversion
outputs more than 255 bytes.

The flaw happens because the floating point conversion is using system
functions without the correct boundary checks.

The functions have been documented as deprecated for a long time and users are
discouraged from using them in "new programs" as they are planned to get
removed at a future point. Since the functions are present and there is
nothing preventing users from using them, we expect there to be a certain
amount of existing users in the wild.

If there are any application that accepts a format string from the outside
without necessary input filtering, it could allow remote attacks.

This flaw does not exist in the command line tool.
