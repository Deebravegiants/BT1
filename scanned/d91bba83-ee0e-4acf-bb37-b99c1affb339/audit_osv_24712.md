# [H] JSON Injection in DataHub

## Summary
Severity: High
Advisory: CVE-2023-25560
Aliases: GHSA-6rpf-5cfg-h8f3
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2023-02-10
Source: https://osv.dev/vulnerability/CVE-2023-25560
Type: osv

## Details
DataHub is an open-source metadata platform. The AuthServiceClient which is responsible for creation of new accounts, verifying credentials, resetting them or requesting access tokens, crafts multiple JSON strings using format strings with user-controlled data. This means that an attacker may be able to augment these JSON strings to be sent to the backend and that can potentially be abused by including new or colliding values. This issue may lead to an authentication bypass and the creation of system accounts, which effectively can lead to full system compromise. Users are advised to upgrade. There are no known workarounds for this vulnerability. This vulnerability was discovered and reported by the GitHub Security lab and is tracked as GHSL-2022-080.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25560.json
- https://github.com/datahub-project/datahub/security/advisories/GHSA-6rpf-5cfg-h8f3
- https://nvd.nist.gov/vuln/detail/CVE-2023-25560
