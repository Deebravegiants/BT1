# [M] Cross-site Scripting (XSS) in UrlSlug Data type

## Summary
Severity: Medium
Advisory: GHSA-x5j3-mq9g-8jc8
CVE: CVE-2023-28106
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-17
Source: https://github.com/advisories/GHSA-x5j3-mq9g-8jc8
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.19

## Details
### Impact
An attacker can use XSS to send a malicious script to an unsuspecting user.

### Patches
Update to version 10.5.19 or apply this patch manually https://github.com/pimcore/pimcore/pull/14669.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/14669.patch manually.

### References
https://huntr.dev/bounties/fa77d780-9b23-404b-8c44-12108881d11a

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-x5j3-mq9g-8jc8
- https://nvd.nist.gov/vuln/detail/CVE-2023-28106
- https://github.com/pimcore/pimcore/pull/14669.patch
- https://github.com/pimcore/pimcore/commit/c59d0bf1d03a5037b586fe06230694fa3818dbf2
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/fa77d780-9b23-404b-8c44-12108881d11a
