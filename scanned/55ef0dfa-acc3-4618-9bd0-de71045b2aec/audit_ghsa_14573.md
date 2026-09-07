# [M] Pimcore vulnerable to Cross-site Scripting (XSS) in Redirects

## Summary
Severity: Medium
Advisory: GHSA-66cm-c7ch-5j8q
CVE: CVE-2023-1515
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-20
Source: https://github.com/advisories/GHSA-66cm-c7ch-5j8q
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.19

## Details
### Impact
Stored XSS vulnerability at Expiry field in the Redirects module.

This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.19 or apply this patch manually https://github.com/pimcore/pimcore/pull/14562.patch

### Workarounds
Apply patch manually https://github.com/pimcore/pimcore/pull/14562.patch

### References
https://huntr.dev/bounties/ae0f2ec4-a245-4d0b-9d4d-bd8310dd6282/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-66cm-c7ch-5j8q
- https://nvd.nist.gov/vuln/detail/CVE-2023-1515
- https://github.com/pimcore/pimcore/pull/14562
- https://github.com/pimcore/pimcore/pull/14562.patch
- https://github.com/pimcore/pimcore/commit/44c6b37aa649a0e3105fa41f3d74a3e511acf964
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/ae0f2ec4-a245-4d0b-9d4d-bd8310dd6282
