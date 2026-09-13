# [H] sandbox-accounts-for-events security misconfiguration leads to budget exceed

## Summary
Severity: High
Advisory: CVE-2023-50928
Aliases: GHSA-cg8w-7q5v-g32r
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L)
Published: 2023-12-22
Source: https://osv.dev/vulnerability/CVE-2023-50928
Type: osv

## Details
"Sandbox Accounts for Events" provides multiple, temporary AWS accounts to a number of authenticated users simultaneously via a browser-based GUI. Authenticated users could potentially claim and access empty AWS accounts by sending request payloads to the account API containing non-existent event ids and self-defined budget & duration. This issue only affects cleaned AWS accounts, it is not possible to access AWS accounts in use or existing data/infrastructure. This issue has been patched in version 1.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50928.json
- https://github.com/awslabs/sandbox-accounts-for-events/security/advisories/GHSA-cg8w-7q5v-g32r
- https://nvd.nist.gov/vuln/detail/CVE-2023-50928
- https://github.com/awslabs/sandbox-accounts-for-events/commit/f30a0662f0a28734eb33c5868cccc1c319eb6e79
