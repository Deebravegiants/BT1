# [C] CVE-2020-15473

## Summary
Severity: Critical
Advisory: CVE-2020-15473
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-07-01
Source: https://osv.dev/vulnerability/CVE-2020-15473
Type: osv

## Details
In nDPI through 3.2, the OpenVPN dissector is vulnerable to a heap-based buffer over-read in ndpi_search_openvpn in lib/protocols/openvpn.c.

## References
- https://github.com/fuzzing2026/CVE-PoCs/tree/main/ndpi-CVE-2020-15473
- https://github.com/ntop/nDPI/commit/8e7b1ea7a136cc4e4aa9880072ec2d69900a825e
