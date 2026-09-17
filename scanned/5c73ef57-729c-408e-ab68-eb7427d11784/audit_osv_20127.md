# [M] CVE-2021-31259

## Summary
Severity: Medium
Advisory: CVE-2021-31259
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-31259
Type: osv

## Details
The gf_isom_cenc_get_default_info_internal function in GPAC 1.0.1 allows attackers to cause a denial of service (NULL pointer dereference) via a crafted file in the MP4Box command.

## References
- https://github.com/gpac/gpac/commit/3b84ffcbacf144ce35650df958432f472b6483f8
- https://github.com/gpac/gpac/issues/1735
