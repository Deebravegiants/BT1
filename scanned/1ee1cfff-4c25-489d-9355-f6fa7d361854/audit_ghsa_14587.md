# [M] Cross-site Scripting (XSS) in Document Types

## Summary
Severity: Medium
Advisory: GHSA-3223-w774-99fq
CVE: CVE-2023-1429
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-16
Source: https://github.com/advisories/GHSA-3223-w774-99fq
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.19

## Details
### Impact
Unsecured Name field in Document Types module in Settings.

This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.19 or apply this patch manually https://github.com/pimcore/pimcore/pull/14645.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/14645.patch manually.

### References
https://huntr.dev/bounties/e0829fea-e458-47b8-84a3-a74476d9638f/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-3223-w774-99fq
- https://nvd.nist.gov/vuln/detail/CVE-2023-1429
- https://github.com/pimcore/pimcore/commit/7588c336edb24050656111b89d69e69cc9feb5f5
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/e0829fea-e458-47b8-84a3-a74476d9638f
