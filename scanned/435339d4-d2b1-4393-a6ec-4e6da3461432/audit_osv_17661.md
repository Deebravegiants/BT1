# [M] CVE-2020-18775

## Summary
Severity: Medium
Advisory: CVE-2020-18775
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/CVE-2020-18775
Type: osv

## Details
In Libav 12.3, there is a heap-based buffer over-read in vc1_decode_b_mb_intfi in vc1_block.c that allows an attacker to cause denial-of-service via a crafted file.

## References
- https://bugzilla.libav.org/show_bug.cgi?id=1152
- https://cwe.mitre.org/data/definitions/126.html
