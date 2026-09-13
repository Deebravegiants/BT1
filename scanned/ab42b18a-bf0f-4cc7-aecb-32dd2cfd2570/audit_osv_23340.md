# [C] CVE-2022-48006

## Summary
Severity: Critical
Advisory: CVE-2022-48006
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-30
Source: https://osv.dev/vulnerability/CVE-2022-48006
Type: osv

## Details
An arbitrary file upload vulnerability in taocms v3.0.2 allows attackers to execute arbitrary code via a crafted PHP file. This vulnerability is exploited via manipulation of the upext variable at /include/Model/Upload.php.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48006.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48006
- https://github.com/taogogo/taocms/issues/35
