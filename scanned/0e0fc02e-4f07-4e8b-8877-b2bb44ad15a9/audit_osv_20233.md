# [H] CVE-2021-32439

## Summary
Severity: High
Advisory: CVE-2021-32439
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-11
Source: https://osv.dev/vulnerability/CVE-2021-32439
Type: osv

## Details
Buffer overflow in the stbl_AppendSize function in MP4Box in GPAC 1.0.1 allows attackers to cause a denial of service or execute arbitrary code via a crafted file.

## References
- https://github.com/gpac/gpac/issues/1774
- https://github.com/gpac/gpac/commit/77ed81c069e10b3861d88f72e1c6be1277ee7eae
