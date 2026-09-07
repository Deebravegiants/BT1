# [M] Pimcore Cross-site Scripting (XSS) vulnerability in DataObject datetime fields

## Summary
Severity: Medium
Advisory: GHSA-599v-h3q5-g6r9
CVE: CVE-2023-4453
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-21
Source: https://github.com/advisories/GHSA-599v-h3q5-g6r9
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.6.8

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.6.8 or apply this patch manually https://github.com/pimcore/pimcore/commit/234c0c02ea7502071b00ab673fbe4a6ac253080e.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/234c0c02ea7502071b00ab673fbe4a6ac253080e.patch manually.

### References
https://huntr.dev/bounties/245a8785-0fc0-4561-b181-fa20f869d993/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-599v-h3q5-g6r9
- https://nvd.nist.gov/vuln/detail/CVE-2023-4453
- https://github.com/pimcore/pimcore/commit/234c0c02ea7502071b00ab673fbe4a6ac253080e
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/245a8785-0fc0-4561-b181-fa20f869d993
