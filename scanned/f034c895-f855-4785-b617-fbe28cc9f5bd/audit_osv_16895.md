# [M] CVE-2020-10575

## Summary
Severity: Medium
Advisory: CVE-2020-10575
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2020-03-14
Source: https://osv.dev/vulnerability/CVE-2020-10575
Type: osv

## Details
An issue was discovered in Janus through 0.9.1. plugins/janus_videocall.c in the VideoCall plugin mishandles session management because a race condition causes some references to be freed too early or too many times.

## References
- https://github.com/meetecho/janus-gateway/pull/1994
