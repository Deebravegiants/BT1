# [H] CVE-2018-15503

## Summary
Severity: High
Advisory: CVE-2018-15503
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-18
Source: https://osv.dev/vulnerability/CVE-2018-15503
Type: osv

## Details
The unpack implementation in Swoole version 4.0.4 lacks correct size checks in the deserialization process. An attacker can craft a serialized object to exploit this vulnerability and cause a SEGV.

## References
- https://x-c3ll.github.io/posts/swoole-deserialization-cve-2018-15503/
- https://github.com/swoole/swoole-src/issues/1882
- https://github.com/swoole/swoole-src/commit/4cdbce5d9bf2fe596bb6acd7d6611f9e8c253a76
