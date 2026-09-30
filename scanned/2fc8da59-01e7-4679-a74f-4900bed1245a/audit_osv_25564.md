# [H] Missing Authorization check allows certain operations on CLA Assistant data

## Summary
Severity: High
Advisory: CVE-2023-39438
Aliases: GHSA-gw8p-frwv-25gh
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-08-15
Source: https://osv.dev/vulnerability/CVE-2023-39438
Type: osv

## Details
A missing authorization check allows an arbitrary authenticated user to perform certain operations through the API of CLA-assistant by executing specific additional steps. This allows an arbitrary authenticated user to read CLA information including information of the persons who signed them as well as custom fields the CLA requester had configured. In addition, an arbitrary authenticated user can update or delete the CLA-configuration for repositories or organizations using CLA-assistant. The stored access tokens for GitHub are not affected, as these are redacted from the API-responses.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39438.json
- https://github.com/cla-assistant/cla-assistant/security/advisories/GHSA-gw8p-frwv-25gh
- https://nvd.nist.gov/vuln/detail/CVE-2023-39438
