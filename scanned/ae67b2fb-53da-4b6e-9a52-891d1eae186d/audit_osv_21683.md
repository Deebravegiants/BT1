# [M] CVE-2021-45292

## Summary
Severity: Medium
Advisory: CVE-2021-45292
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-12-21
Source: https://osv.dev/vulnerability/CVE-2021-45292
Type: osv

## Details
The gf_isom_hint_rtp_read function in GPAC 1.0.1 allows attackers to cause a denial of service (Invalid memory address dereference) via a crafted file in the MP4Box command.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1958
