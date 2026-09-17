# [M] CVE-2018-19888

## Summary
Severity: Medium
Advisory: CVE-2018-19888
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-06
Source: https://osv.dev/vulnerability/CVE-2018-19888
Type: osv

## Details
An invalid memory address dereference was discovered in the huffcode function (libfaac/huff2.c) in Freeware Advanced Audio Coder (FAAC) 1.29.9.2. The vulnerability causes a segmentation fault and application crash, which leads to denial of service in the HCB_ESC case.

## References
- https://github.com/knik0/faac/issues/25
