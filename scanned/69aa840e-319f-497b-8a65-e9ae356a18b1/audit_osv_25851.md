# [M] CVE-2023-46001

## Summary
Severity: Medium
Advisory: CVE-2023-46001
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-11-07
Source: https://osv.dev/vulnerability/CVE-2023-46001
Type: osv

## Details
Buffer Overflow vulnerability in gpac MP4Box v.2.3-DEV-rev573-g201320819-master allows a local attacker to cause a denial of service via the gpac/src/isomedia/isom_read.c:2807:51 function in gf_isom_get_user_data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46001.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-46001
- https://github.com/gpac/gpac/issues/2629
- https://github.com/gpac/gpac/commit/e79b0cf7e72404750630bc01340e999f3940dbc4
