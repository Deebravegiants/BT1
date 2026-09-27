# [M] CVE-2021-36584

## Summary
Severity: Medium
Advisory: CVE-2021-36584
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-05
Source: https://osv.dev/vulnerability/CVE-2021-36584
Type: osv

## Details
An issue was discovered in GPAC 1.0.1. There is a heap-based buffer overflow in the function gp_rtp_builder_do_tx3g function in ietf/rtp_pck_3gpp.c, as demonstrated by MP4Box. This can cause a denial of service (DOS).

## References
- https://github.com/gpac/gpac/issues/1842
