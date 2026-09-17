# [C] CVE-2018-8785

## Summary
Severity: Critical
Advisory: CVE-2018-8785
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-8785
Type: osv

## Details
FreeRDP prior to version 2.0.0-rc4 contains a Heap-Based Buffer Overflow in function zgfx_decompress() that results in a memory corruption and probably even a remote code execution.

## References
- http://www.securityfocus.com/bid/106938
- https://usn.ubuntu.com/3845-1/
- https://github.com/FreeRDP/FreeRDP/commit/602f4a2e14b41703b5f431de3154cd46a5750a2d
- https://research.checkpoint.com/reverse-rdp-attack-code-execution-on-rdp-clients/
