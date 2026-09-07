# [M] Pimcore has Cross-site Scripting vulnerability in DataObject tooltip field

## Summary
Severity: Medium
Advisory: GHSA-rcg9-hrhx-6q69
CVE: CVE-2023-28429
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-20
Source: https://github.com/advisories/GHSA-rcg9-hrhx-6q69
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.19

## Details
### Impact
Unsecured tooltip field in DataObject class definition.

This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.19 or apply this patch manually https://github.com/pimcore/pimcore/pull/14574.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/14574.patch manually.

### References

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-rcg9-hrhx-6q69
- https://nvd.nist.gov/vuln/detail/CVE-2023-28429
- https://github.com/pimcore/pimcore/pull/14574
- https://github.com/pimcore/pimcore/pull/14574.patch
- https://github.com/pimcore/pimcore
