# [H] CVE-2023-26917

## Summary
Severity: High
Advisory: CVE-2023-26917
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-11
Source: https://osv.dev/vulnerability/CVE-2023-26917
Type: osv

## Details
libyang from v2.0.164 to v2.1.30 was discovered to contain a NULL pointer dereference via the function lysp_stmt_validate_value at lys_parse_mem.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26917.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26917
- https://github.com/CESNET/libyang/issues/1987
