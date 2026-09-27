# [M] Record titles for restricted records can be viewed if exposed by GridFieldAddExistingAutocompleter

## Summary
Severity: Medium
Advisory: GHSA-qm2j-qvq3-j29v
CVE: CVE-2023-48714
CWE: CWE-200, CWE-732
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-01-23
Source: https://github.com/advisories/GHSA-qm2j-qvq3-j29v
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <4.13.39
- Packagist: `silverstripe/framework` — affected >=5.0.0 <5.1.11

## Details
### Impact
If a user should not be able to see a record, but that record can be added to a `GridField` using the `GridFieldAddExistingAutocompleter` component, the record's title can be accessed by that user.

**Base CVSS:** [4.3](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N/E:F/RL:O/RC:C&version=3.1)
**Reported by:** Nick K - LittleMonkey, [littlemonkey.co.nz](http://littlemonkey.co.nz/)

### References
- https://www.silverstripe.org/download/security-releases/CVE-2023-48714

## References
- https://github.com/silverstripe/silverstripe-framework/security/advisories/GHSA-qm2j-qvq3-j29v
- https://nvd.nist.gov/vuln/detail/CVE-2023-48714
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2023-48714.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/CVE-2023-48714
