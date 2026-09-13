# [H] CVE-2019-12101

## Summary
Severity: High
Advisory: CVE-2019-12101
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-15
Source: https://osv.dev/vulnerability/CVE-2019-12101
Type: osv

## Details
coap_decode_option in coap.c in LibNyoci 0.07.00rc1 mishandles certain packets with "Uri-Path: (null)" and consequently allows remote attackers to cause a denial of service (segmentation fault).

## References
- https://github.com/darconeous/libnyoci/issues/21
