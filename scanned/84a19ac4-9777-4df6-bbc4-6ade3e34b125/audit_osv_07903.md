# [M] FTP-KRB double free

## Summary
Severity: Medium
Advisory: CURL-CVE-2019-5481
Aliases: CVE-2019-5481
Published: 2019-09-11
Source: https://osv.dev/vulnerability/CURL-CVE-2019-5481
Type: osv

## Details
libcurl can be told to use kerberos over FTP to a server, as set with the
`CURLOPT_KRBLEVEL` option.

During such kerberos FTP data transfer, the server sends data to curl in
blocks with the 32-bit size of each block first and then that amount of data
immediately following.

A malicious or broken server can claim to send a large block and if by doing
that it makes curl's subsequent call to `realloc()` to fail, curl would then
misbehave in the exit path and double free the memory.

In practical terms, an up to 4 GB memory area may well be fine to allocate
on a modern 64-bit system but on 32-bit systems it fails.

Kerberos FTP is a rarely used protocol with curl. Also, Kerberos
authentication is usually only attempted and used with servers that the client
has a previous association with.
