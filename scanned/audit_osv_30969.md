# [C] CVE-2024-57032

## Summary
Severity: Critical
Advisory: CVE-2024-57032
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-17
Source: https://osv.dev/vulnerability/CVE-2024-57032
Type: osv

## Details
WeGIA < 3.2.0 is vulnerable to Incorrect Access Control in controle/control.php. The application does not validate the value of the old password, so it is possible to change the password by placing any value in the senha_antiga field.

## References
- https://github.com/nmmorette/vulnerability-research/blob/main/CVE-2024-57032
- https://www.wegia.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57032.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57032
