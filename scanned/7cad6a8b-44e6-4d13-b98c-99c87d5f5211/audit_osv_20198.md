# [M] CVE-2021-32134

## Summary
Severity: Medium
Advisory: CVE-2021-32134
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-13
Source: https://osv.dev/vulnerability/CVE-2021-32134
Type: osv

## Details
The gf_odf_desc_copy function in GPAC 1.0.1 allows attackers to cause a denial of service (NULL pointer dereference) via a crafted file in the MP4Box command.

## References
- https://github.com/gpac/gpac/commit/328c6d682698fdb9878dbb4f282963d42c538c01
- https://github.com/gpac/gpac/issues/1756
