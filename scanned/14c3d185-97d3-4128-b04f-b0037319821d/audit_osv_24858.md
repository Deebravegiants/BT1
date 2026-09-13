# [H] CVE-2023-27728

## Summary
Severity: High
Advisory: CVE-2023-27728
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-09
Source: https://osv.dev/vulnerability/CVE-2023-27728
Type: osv

## Details
Nginx NJS v0.7.10 was discovered to contain a segmentation violation via the function njs_dump_is_recursive at src/njs_vmcode.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27728.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-27728
- https://github.com/nginx/njs/issues/618
