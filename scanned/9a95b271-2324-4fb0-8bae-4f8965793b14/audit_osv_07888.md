# [M] FTP PWD response parser out of bounds read

## Summary
Severity: Medium
Advisory: CURL-CVE-2017-1000254
Aliases: CVE-2017-1000254
Published: 2017-10-04
Source: https://osv.dev/vulnerability/CURL-CVE-2017-1000254
Type: osv

## Details
libcurl may read outside of a heap allocated buffer when doing FTP.

When libcurl connects to an FTP server and successfully logs in (anonymous or
not), it asks the server for the current directory with the `PWD` command. The
server then responds with a 257 response containing the path, inside double
quotes. The returned path name is then kept by libcurl for subsequent uses.

Due to a flaw in the string parser for this directory name, a directory name
passed like this but without a closing double quote would lead to libcurl not
adding a trailing null byte to the buffer holding the name. When libcurl would
then later access the string, it could read beyond the allocated heap buffer
and crash or wrongly access data beyond the buffer, thinking it was part of
the path.

A malicious server could abuse this fact and effectively prevent libcurl-based
clients to work with it - the PWD command is always issued on new FTP
connections and the mistake has a high chance of causing a segfault.

The simple fact that this issue has remained undiscovered for this long could
suggest that malformed PWD responses are rare in benign servers.
