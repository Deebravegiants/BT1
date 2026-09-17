# [H] TFTP sends more than buffer size

## Summary
Severity: High
Advisory: CURL-CVE-2017-1000100
Aliases: CVE-2017-1000100
Published: 2017-08-09
Source: https://osv.dev/vulnerability/CURL-CVE-2017-1000100
Type: osv

## Details
When doing a TFTP transfer and curl/libcurl is given a URL that contains a
long filename (longer than about 515 bytes), the filename is truncated to fit
within the buffer boundaries, but the buffer size is still wrongly updated
to use the original length. This too large value is then used in the
`sendto()` call, making curl attempt to send more data than what is actually
put into the buffer. The `sendto()` function then reads beyond the end of the
heap based buffer.

A malicious HTTP(S) server could redirect a vulnerable libcurl-using client to
a crafted TFTP URL (if the client has not restricted which protocols it allows
redirects to) and trick it to send private memory contents to a remote server
over UDP. Limit curl's redirect protocols with `--proto-redir` and libcurl's
with `CURLOPT_REDIR_PROTOCOLS`.
