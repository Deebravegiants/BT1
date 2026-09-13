# [M] CVE-2021-32139

## Summary
Severity: Medium
Advisory: CVE-2021-32139
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-13
Source: https://osv.dev/vulnerability/CVE-2021-32139
Type: osv

## Details
The gf_isom_vp_config_get function in GPAC 1.0.1 allows attackers to cause a denial of service (NULL pointer dereference) via a crafted file in the MP4Box command.

## References
- https://github.com/gpac/gpac/commit/d527325a9b72218612455a534a508f9e1753f76e
- https://github.com/gpac/gpac/issues/1768
