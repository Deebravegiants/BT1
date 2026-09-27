# [C] Remote Code Execution in Contao Managed Edition

## Summary
Severity: Critical
Advisory: GHSA-rggc-4g3r-j7ff
CVE: CVE-2022-26265
CWE: CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-20
Source: https://github.com/advisories/GHSA-rggc-4g3r-j7ff
Type: github-advisory

## Affected
- Packagist: `contao/managed-edition` — affected >=0

## Details
Contao Managed Edition v1.5.0 was discovered to contain a remote command execution (RCE) vulnerability via the component php_cli parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26265
- https://github.com/JCCD/Contao-Managed-Edition-1.5-RCE/blob/main/VulnerabilityDetails.md
- https://github.com/contao/managed-edition
