# [M] CVE-2020-11038

## Summary
Severity: Medium
Advisory: CVE-2020-11038
Aliases: GHSA-h25x-cqr6-fp6g
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2020-05-29
Source: https://osv.dev/vulnerability/CVE-2020-11038
Type: osv

## Details
In FreeRDP less than or equal to 2.0.0, an Integer Overflow to Buffer Overflow exists. When using /video redirection, a manipulated server can instruct the client to allocate a buffer with a smaller size than requested due to an integer overflow in size calculation. With later messages, the server can manipulate the client to write data out of bound to the previously allocated buffer. This has been patched in 2.1.0.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-h25x-cqr6-fp6g
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
