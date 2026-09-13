# [H] CVE-2019-14323

## Summary
Severity: High
Advisory: CVE-2019-14323
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-28
Source: https://osv.dev/vulnerability/CVE-2019-14323
Type: osv

## Details
SSDP Responder 1.x through 1.5 mishandles incoming network messages, leading to a stack-based buffer overflow by 1 byte. This results in a crash of the server, but only when strict stack checking is enabled. This is caused by an off-by-one error in ssdp_recv in ssdpd.c.

## References
- https://github.com/troglobit/ssdp-responder/commit/ce04b1f29a137198182f60bbb628d5ceb8171765
- https://github.com/troglobit/ssdp-responder/issues/1
