# [M] XSS Injection in Media Collection Title was possible

## Summary
Severity: Medium
Advisory: GHSA-gm2x-6475-g9r8
CVE: CVE-2021-32737
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-07-02
Source: https://github.com/advisories/GHSA-gm2x-6475-g9r8
Type: github-advisory

## Affected
- Packagist: `sulu/sulu` — affected >=0 <1.6.41

## Details
### Impact

A logged in admin user was possible to add a script injection (XSS) in the collection title which was executed.

### Workarounds

Manual patching the js files.

### For more information

If you have any questions or comments about this advisory:'

 - Email us at [security@sulu.io](mailto:security@sulu.io)

## References
- https://github.com/sulu/sulu/security/advisories/GHSA-gm2x-6475-g9r8
- https://nvd.nist.gov/vuln/detail/CVE-2021-32737
- https://github.com/sulu/sulu/releases/tag/1.6.41
