# [C] CVE-2018-8784

## Summary
Severity: Critical
Advisory: CVE-2018-8784
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-8784
Type: osv

## Details
FreeRDP prior to version 2.0.0-rc4 contains a Heap-Based Buffer Overflow in function zgfx_decompress_segment() that results in a memory corruption and probably even a remote code execution.

## References
- http://www.securityfocus.com/bid/106938
- https://usn.ubuntu.com/3845-1/
- https://github.com/FreeRDP/FreeRDP/commit/17c363a5162fd4dc77b1df54e48d7bd9bf6b3be7
- https://research.checkpoint.com/reverse-rdp-attack-code-execution-on-rdp-clients/
