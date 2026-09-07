# [H] Improper Encoding or Escaping of Output in Asset Metadata Component

## Summary
Severity: High
Advisory: GHSA-2v88-qq7x-xq5f
CVE: CVE-2021-39170
CWE: CWE-116, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-2v88-qq7x-xq5f
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.1.2

## Details
Pimcore is an open source data & experience management platform. Prior to version 10.1.2, an authenticated user could add XSS code as a value of custom metadata on assets. There is a patch for this issue in Pimcore version 10.1.2. As a workaround, users may apply the patch manually.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-2v88-qq7x-xq5f
- https://nvd.nist.gov/vuln/detail/CVE-2021-39170
- https://github.com/pimcore/pimcore/pull/10178
- https://github.com/pimcore/pimcore/pull/10178.patch
- https://github.com/pimcore/pimcore/pull/10206
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/c3e4cf79-a4b5-4982-af27-729f66281501
- https://huntr.dev/bounties/e4cb9cd8-89cf-427c-8d2e-37ca40099bf2
