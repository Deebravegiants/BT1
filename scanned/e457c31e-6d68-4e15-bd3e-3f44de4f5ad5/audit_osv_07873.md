# [H] cookie injection for other servers

## Summary
Severity: High
Advisory: CURL-CVE-2016-8615
Aliases: CVE-2016-8615
Published: 2016-11-02
Source: https://osv.dev/vulnerability/CURL-CVE-2016-8615
Type: osv

## Details
If cookie state is written into a cookie jar file that is later read back and
used for subsequent requests, a malicious HTTP server can inject new cookies
for arbitrary domains into said cookie jar.

The issue pertains to the function that loads cookies into memory, which reads
the specified file into a fixed-size buffer in a line-by-line manner using the
`fgets()` function. If an invocation of `fgets()` cannot read the whole line
into the destination buffer due to it being too small, it truncates the
output. This way, a long cookie (name + value) sent by a malicious server
would be stored in the file and subsequently that cookie could be read
partially and crafted correctly, it could be treated as a different cookie for
another server.
