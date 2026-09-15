# [C] CVE-2024-39010

## Summary
Severity: Critical
Advisory: CVE-2024-39010
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-39010
Type: osv

## Details
chase-moskal snapstate v0.0.9 was discovered to contain a prototype pollution via the function attemptNestedProperty. This vulnerability allows attackers to execute arbitrary code or cause a Denial of Service (DoS) via injecting arbitrary properties.

## References
- https://gist.github.com/mestrtee/af7a746df91ab5e944bd7a186816c262
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39010.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39010
