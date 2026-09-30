# [M] Corveda PHPSandbox Protection Mechanism Failure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-625p-jwcp-r2r5
CVE: CVE-2014-125107
CWE: CWE-693
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-12-19
Source: https://github.com/advisories/GHSA-625p-jwcp-r2r5
Type: github-advisory

## Affected
- Packagist: `corveda/phpsandbox` — affected >=0 <1.3.5

## Details
A vulnerability was found in Corveda PHPSandbox 1.3.4 and classified as critical. Affected by this issue is some unknown functionality of the component String Handler. The manipulation leads to protection mechanism failure. The attack may be launched remotely. Upgrading to version 1.3.5 is able to address this issue. The patch is identified as 48fde5ffa4d76014bad260a3cbab7ada3744a4cc. It is recommended to upgrade the affected component. VDB-248270 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-125107
- https://github.com/Corveda/PHPSandbox/commit/48fde5ffa4d76014bad260a3cbab7ada3744a4cc
- https://github.com/Corveda/PHPSandbox
- https://github.com/Corveda/PHPSandbox/releases/tag/v1.3.5
- https://vuldb.com/?ctiid.248270
- https://vuldb.com/?id.248270
