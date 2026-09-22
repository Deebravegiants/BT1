# [H] CVE-2021-33362

## Summary
Severity: High
Advisory: CVE-2021-33362
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-09-13
Source: https://osv.dev/vulnerability/CVE-2021-33362
Type: osv

## Details
Stack buffer overflow in the hevc_parse_vps_extension function in MP4Box in GPAC 1.0.1 allows attackers to cause a denial of service or execute arbitrary code via a crafted file.

## References
- https://github.com/gpac/gpac/commit/1273cdc706eeedf8346d4b9faa5b33435056061d
- https://github.com/gpac/gpac/issues/1780
