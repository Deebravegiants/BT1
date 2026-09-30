# [H] CVE-2016-10518

## Summary
Severity: High
Advisory: CVE-2016-10518
Aliases: GHSA-2mhh-w6q8-5hxw
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-05-31
Source: https://osv.dev/vulnerability/CVE-2016-10518
Type: osv

## Details
A vulnerability was found in the ping functionality of the ws module before 1.0.0 which allowed clients to allocate memory by sending a ping frame. The ping functionality by default responds with a pong frame and the previously given payload of the ping frame. This is exactly what you expect, but internally ws always transforms all data that we need to send to a Buffer instance and that is where the vulnerability existed. ws didn't do any checks for the type of data it was sending. With buffers in node when you allocate it when a number instead of a string it will allocate the amount of bytes.

## References
- https://github.com/websockets/ws/releases/tag/1.0.1
- https://nodesecurity.io/advisories/67
- https://gist.github.com/c0nrad/e92005446c480707a74a
