# [H] CVE-2024-31755

## Summary
Severity: High
Advisory: CVE-2024-31755
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-04-26
Source: https://osv.dev/vulnerability/CVE-2024-31755
Type: osv

## Details
cJSON v1.7.17 was discovered to contain a segmentation violation, which can trigger through the second parameter of function cJSON_SetValuestring at cJSON.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31755.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-31755
- https://github.com/DaveGamble/cJSON/issues/839
