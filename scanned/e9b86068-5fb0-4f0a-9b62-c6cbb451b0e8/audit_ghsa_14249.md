# [M] Cross-site Scripting (XSS) in Ecommerce Pricing Rules name field

## Summary
Severity: Medium
Advisory: GHSA-cjv6-w5hf-5wr6
CVE: CVE-2023-2323
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-cjv6-w5hf-5wr6
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.21 or apply this patch manually https://github.com/pimcore/pimcore/commit/e88fa79de7b5903fb58ddbc231130b04d937d79e.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/e88fa79de7b5903fb58ddbc231130b04d937d79e.patch manually.

### References
https://huntr.dev/bounties/41edf190-f6bf-4a29-a237-7ff1b2d048d3/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-cjv6-w5hf-5wr6
- https://nvd.nist.gov/vuln/detail/CVE-2023-2323
- https://github.com/pimcore/pimcore/commit/e88fa79de7b5903fb58ddbc231130b04d937d79e
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/41edf190-f6bf-4a29-a237-7ff1b2d048d3
