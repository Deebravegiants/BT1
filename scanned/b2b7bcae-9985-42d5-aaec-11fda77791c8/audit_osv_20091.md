# [M] CVE-2021-30199

## Summary
Severity: Medium
Advisory: CVE-2021-30199
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-30199
Type: osv

## Details
In filters/reframe_latm.c in GPAC 1.0.1 there is a Null Pointer Dereference, when gf_filter_pck_get_data is called. The first arg pck may be null with a crafted mp4 file,which results in a crash.

## References
- https://github.com/gpac/gpac/commit/b2db2f99b4c30f96e17b9a14537c776da6cb5dca
- https://github.com/gpac/gpac/issues/1728
