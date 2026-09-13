# [M] Netty's HttpPostRequestDecoder can OOM

## Summary
Severity: Medium
Advisory: GHSA-5jpm-x58v-624v
CVE: CVE-2024-29025
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-5jpm-x58v-624v
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=0 <4.1.108.Final

## Details
### Summary
The `HttpPostRequestDecoder` can be tricked to accumulate data. I have spotted currently two attack vectors 

### Details
1. While the decoder can store items on the disk if configured so, there are no limits to the number of fields the form can have, an attacher can send a chunked post consisting of many small fields that will be accumulated in the `bodyListHttpData` list.
2. The decoder cumulates bytes in the `undecodedChunk` buffer until it can decode a field, this field can cumulate data without limits

### PoC

Here is a Netty branch that provides a fix + tests : https://github.com/vietj/netty/tree/post-request-decoder


Here is a reproducer with Vert.x (which uses this decoder) https://gist.github.com/vietj/f558b8ea81ec6505f1e9a6ca283c9ae3

### Impact
Any Netty based HTTP server that uses the `HttpPostRequestDecoder` to decode a form.

## References
- https://github.com/netty/netty/security/advisories/GHSA-5jpm-x58v-624v
- https://nvd.nist.gov/vuln/detail/CVE-2024-29025
- https://github.com/netty/netty/commit/0d0c6ed782d13d423586ad0c71737b2c7d02058c
- https://gist.github.com/vietj/f558b8ea81ec6505f1e9a6ca283c9ae3
- https://github.com/netty/netty
- https://github.com/vietj/netty/tree/post-request-decoder
- https://lists.debian.org/debian-lts-announce/2024/06/msg00015.html
