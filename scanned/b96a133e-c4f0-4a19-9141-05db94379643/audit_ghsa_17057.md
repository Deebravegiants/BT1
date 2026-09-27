# [H] Deno's Node.js Compatibility Runtime has Cross-Session Data Contamination

## Summary
Severity: High
Advisory: GHSA-wrqv-pf6j-mqjp
CVE: CVE-2024-27935
CWE: CWE-488
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2024-03-05
Source: https://github.com/advisories/GHSA-wrqv-pf6j-mqjp
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=1.35.1 <1.36.3

## Details
### Summary

A vulnerability in Deno's Node.js compatibility runtime allows for cross-session data contamination during simultaneous asynchronous reads from Node.js streams sourced from sockets or files. The issue arises from the re-use of a global buffer (BUF) in stream_wrap.ts used as a performance optimization to limit allocations during these asynchronous read operations. This can lead to data intended for one session being received by another session, potentially resulting in data corruption and unexpected behavior.

### Details

A bug in Deno's Node.js compatibility runtime results in data cross-reception during simultaneous asynchronous reads from Node.js network streams. When multiple independent network socket connections are involved, this vulnerability can be triggered. For instance, two separate server sockets that receive data from their respective client sockets and then echo the received data back to the client using Node.js streams may experience an issue where data from one socket may appear on another socket. Due to the improper isolation of the global buffer (`BUF`), data sent by one socket can end up being incorrectly received by another socket. Consequently, data intended for one session may be exposed to another session, potentially leading to data corruption and unexpected behavior.

This buffer was introduced as a performance optimization to avoid excessive allocations during network read operations.

In cases where the [net.Stream](https://nodejs.org/api/net.html) is connected to a remote server such as a database or key/value store such as Redis, this may result in a packet received on one connection being presented to another, causing data cross-contamination between multiple users and potentially leaking sensitive information.

It is important to note that this vulnerability does not affect Deno network streams created with the `Deno.listen` and `Deno.connect` APIs. 

The impact of this issue may extend beyond node.js network streams, however, and may also affect asynchronous reads from non-network node.js Stream such as those created from files.

### PoC

https://github.com/denoland/deno/issues/20188

### Impact

This affects all users of Deno that use the node.js compatibility layer for network communication or other streams, including packages that may require node.js libraries indirectly.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-wrqv-pf6j-mqjp
- https://nvd.nist.gov/vuln/detail/CVE-2024-27935
- https://github.com/denoland/deno/issues/20188
- https://github.com/denoland/deno/commit/3e9fb8aafd9834ebacd27734cea4310caaf794c6
- https://github.com/denoland/deno
