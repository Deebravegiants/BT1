# [C] CVE-2024-57099

## Summary
Severity: Critical
Advisory: CVE-2024-57099
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-03
Source: https://osv.dev/vulnerability/CVE-2024-57099
Type: osv

## Details
ClassCMS v4.8 has a code execution vulnerability. Attackers can exploit this vulnerability by constructing a payload in the classview parameter of the model management feature, allowing them to execute arbitrary code and potentially take control of the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57099.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57099
- https://github.com/ClassCMS/ClassCMS/issues/6
