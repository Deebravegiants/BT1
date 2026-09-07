# [M] Cross-site Scripting (XSS) in DataObject Classification Store

## Summary
Severity: Medium
Advisory: GHSA-9q7q-r54q-3f3g
CVE: CVE-2023-2343
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-9q7q-r54q-3f3g
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.21 or apply this patch manually https://github.com/pimcore/pimcore/commit/f1d904094700b513c4756904fa2b1e19d08d890e.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/f1d904094700b513c4756904fa2b1e19d08d890e.patch manually.

### References
https://huntr.dev/bounties/2fa17227-a717-4b66-ab5a-16bffbb4edb2/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-9q7q-r54q-3f3g
- https://nvd.nist.gov/vuln/detail/CVE-2023-2343
- https://github.com/pimcore/pimcore/commit/f1d904094700b513c4756904fa2b1e19d08d890e
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/2fa17227-a717-4b66-ab5a-16bffbb4edb2
