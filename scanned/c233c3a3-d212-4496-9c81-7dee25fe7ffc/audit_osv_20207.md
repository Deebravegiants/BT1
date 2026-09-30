# [H] CVE-2021-32268

## Summary
Severity: High
Advisory: CVE-2021-32268
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32268
Type: osv

## Details
Buffer overflow vulnerability in function gf_fprintf in os_file.c in gpac before 1.0.1 allows attackers to execute arbitrary code. The fixed version is 1.0.1.

## References
- https://github.com/gpac/gpac/commit/388ecce75d05e11fc8496aa4857b91245007d26e
- https://github.com/gpac/gpac/issues/1587
