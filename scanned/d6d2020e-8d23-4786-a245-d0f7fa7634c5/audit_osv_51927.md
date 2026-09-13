# [M] CVE-2021-45762

## Summary
Severity: Medium
Advisory: CVE-2021-45762
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-14
Source: https://osv.dev/vulnerability/CVE-2021-45762
Type: osv

## Details
GPAC v1.1.0 was discovered to contain an invalid memory address dereference via the function gf_sg_vrml_mf_reset(). This vulnerability allows attackers to cause a Denial of Service (DoS).

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1978
