# [M] FILE buffer read out of bounds

## Summary
Severity: Medium
Advisory: CURL-CVE-2017-1000099
Aliases: CVE-2017-1000099
Published: 2017-08-09
Source: https://osv.dev/vulnerability/CURL-CVE-2017-1000099
Type: osv

## Details
When asking to get a file from a file:// URL, libcurl provides a feature that
outputs meta-data about the file using HTTP-like headers.

The code doing this would send the wrong buffer to the user (stdout or the
application's provide callback), which could lead to other private data from
the heap to get inadvertently displayed.

The wrong buffer was an uninitialized memory area allocated on the heap and if
it turned out to not contain any zero byte, it would continue and display the
data following that buffer in memory.
