# [M] CVE-2021-31258

## Summary
Severity: Medium
Advisory: CVE-2021-31258
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-31258
Type: osv

## Details
The gf_isom_set_extraction_slc function in GPAC 1.0.1 allows attackers to cause a denial of service (NULL pointer dereference) via a crafted file in the MP4Box command.

## References
- https://github.com/gpac/gpac/commit/ebfa346eff05049718f7b80041093b4c5581c24e
- https://github.com/gpac/gpac/issues/1706
