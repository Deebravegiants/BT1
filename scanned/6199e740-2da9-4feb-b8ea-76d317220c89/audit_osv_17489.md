# [C] CVE-2020-15475

## Summary
Severity: Critical
Advisory: CVE-2020-15475
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-01
Source: https://osv.dev/vulnerability/CVE-2020-15475
Type: osv

## Details
In nDPI through 3.2, ndpi_reset_packet_line_info in lib/ndpi_main.c omits certain reinitialization, leading to a use-after-free.

## References
- https://github.com/ntop/nDPI/commit/6a9f5e4f7c3fd5ddab3e6727b071904d76773952
