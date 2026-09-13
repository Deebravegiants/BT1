# [H] CVE-2024-57433

## Summary
Severity: High
Advisory: CVE-2024-57433
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2024-57433
Type: osv

## Details
macrozheng mall-tiny 1.0.1 is vulnerable to Incorrect Access Control via the logout function. After a user logs out, their token is still available and fetches information in the logged-in state.

## References
- https://github.com/peccc/restful_vul/blob/main/mall_tiny_logout_failed/mall_tiny_logout_failed.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57433.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57433
