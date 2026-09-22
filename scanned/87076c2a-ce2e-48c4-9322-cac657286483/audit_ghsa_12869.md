# [M] SUKOHI Surpass Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-c9pw-f4wp-22jr
CVE: CVE-2015-10030
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-01-08
Source: https://github.com/advisories/GHSA-c9pw-f4wp-22jr
Type: github-advisory

## Affected
- Packagist: `sukohi/surpass` — affected >=0 <1.0.0

## Details
A vulnerability has been found in SUKOHI Surpass and classified as critical. This vulnerability affects unknown code of the file `src/Sukohi/Surpass/Surpass.php`. The manipulation of the argument dir leads to pathname traversal. Upgrading to version 1.0.0 can address this issue. The name of the patch is d22337d453a2a14194cdb02bf12cdf9d9f827aa7. It is recommended to upgrade the affected component. VDB-217642 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-10030
- https://github.com/SUKOHI/Surpass/commit/d22337d453a2a14194cdb02bf12cdf9d9f827aa7
- https://github.com/SUKOHI/Surpass
- https://github.com/SUKOHI/Surpass/releases/tag/1.0.0
- https://vuldb.com/?ctiid.217642
- https://vuldb.com/?id.217642
