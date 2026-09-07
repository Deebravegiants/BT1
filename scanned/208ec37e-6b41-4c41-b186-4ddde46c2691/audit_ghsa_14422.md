# [M] Pimcore has Cross site Scripting vulnerability in Schedule tab of Documents

## Summary
Severity: Medium
Advisory: GHSA-42x8-2v53-pqmj
CVE: CVE-2023-1517
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-20
Source: https://github.com/advisories/GHSA-42x8-2v53-pqmj
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.19

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.19 or apply this patch manually https://github.com/pimcore/pimcore/pull/14631.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/14631.patch manually.

### References
https://huntr.dev/bounties/82adf0dd-8ebd-4d15-9f91-6060c8fa5a0d/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-42x8-2v53-pqmj
- https://nvd.nist.gov/vuln/detail/CVE-2023-1517
- https://github.com/pimcore/pimcore/pull/14631
- https://github.com/pimcore/pimcore/pull/14631.patch
- https://github.com/pimcore/pimcore/commit/3a22700dacd8a439cffcb208838a4199e732cff7
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/82adf0dd-8ebd-4d15-9f91-6060c8fa5a0d
