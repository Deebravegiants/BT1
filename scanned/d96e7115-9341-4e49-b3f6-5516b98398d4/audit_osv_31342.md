# [M] Exposure of Sensitive Information in transformeroptimus/superagi

## Summary
Severity: Medium
Advisory: CVE-2024-9447
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-9447
Type: osv

## Details
An information disclosure vulnerability exists in the latest version of transformeroptimus/superagi. The `/get/organisation/` endpoint does not verify the user's organization, allowing any authenticated user to retrieve sensitive configuration details, including API keys, of any organization. This could lead to unauthorized access to services and significant data breaches or financial loss.

## References
- https://huntr.com/bounties/c952ea32-3047-42d3-8a3e-e67899e35dfd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/9xxx/CVE-2024-9447.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-9447
