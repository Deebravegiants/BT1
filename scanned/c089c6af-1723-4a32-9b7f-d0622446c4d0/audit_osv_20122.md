# [H] CVE-2021-31254

## Summary
Severity: High
Advisory: CVE-2021-31254
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-31254
Type: osv

## Details
Buffer overflow in the tenc_box_read function in MP4Box in GPAC 1.0.1 allows attackers to cause a denial of service or execute arbitrary code via a crafted file, related invalid IV sizes.

## References
- https://github.com/gpac/gpac/commit/8986422c21fbd9a7bf6561cae65aae42077447e8
- https://github.com/gpac/gpac/issues/1703
