# [H] Exposure of password hashes in notrinos/notrinos-erp

## Summary
Severity: High
Advisory: GHSA-44w5-q257-8428
CVE: CVE-2022-2921
CWE: CWE-359
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-22
Source: https://github.com/advisories/GHSA-44w5-q257-8428
Type: github-advisory

## Affected
- Packagist: `notrinos/notrinos-erp` — affected >=0 <0.7

## Details
The AP officers account is authorized to Backup and Restore the Database, Due to this he/she can download the backup and see the password hash of the System Administrator account, The weak hash (MD5) of the password can be easily cracked and get the admin password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2921
- https://github.com/notrinos/notrinoserp/commit/1b9903f4deea3289872793e60d730c63ecbf7b45
- https://github.com/notrinos/NotrinosERP
- https://huntr.dev/bounties/51b32a1c-946b-4390-a212-b6c4b6e4115c
