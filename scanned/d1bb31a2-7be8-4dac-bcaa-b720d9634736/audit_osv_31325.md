# [C] Authentication Bypass in composiohq/composio

## Summary
Severity: Critical
Advisory: CVE-2024-8954
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-8954
Type: osv

## Details
In composiohq/composio version 0.5.10, the API does not validate the `x-api-key` header's value during the authentication step. This vulnerability allows an attacker to bypass authentication by providing any random value in the `x-api-key` header, thereby gaining unauthorized access to the server.

## References
- https://huntr.com/bounties/f1e0fdce-00d7-4261-a466-923062800b12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8954.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8954
