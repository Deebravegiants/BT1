# [H] CVE-2021-40570

## Summary
Severity: High
Advisory: CVE-2021-40570
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-01-13
Source: https://osv.dev/vulnerability/CVE-2021-40570
Type: osv

## Details
The binary MP4Box in Gpac 1.0.1 has a double-free vulnerability in the avc_compute_poc function in av_parsers.c, which allows attackers to cause a denial of service, even code execution and escalation of privileges.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1899
- https://github.com/gpac/gpac/commit/04dbf08bff4d61948bab80c3f9096ecc60c7f302
