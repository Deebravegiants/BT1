# [M] SilverStripe Subsite weakens file permissions

## Summary
Severity: Medium
Advisory: GHSA-cx45-565q-6qx8
CVE: CVE-2022-42949
CWE: CWE-732
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-19
Source: https://github.com/advisories/GHSA-cx45-565q-6qx8
Type: github-advisory

## Affected
- Packagist: `silverstripe/subsites` — affected >=2.0.0 <2.6.1

## Details
The subsites module can weaken edit restrictions on some files and allow a malicious user to edit files they do not have edit rights to.

This only affects projects with the subsites module installed. Regression testing should focus on custom file logic.

Be advised that this is not a case of a user being able to edit a file in subsites they do not have access to. As a reminder, all separation of content achieved with the subsites module should be viewed as cosmetic and not appropriate for security-critical applications.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42949
- https://github.com/silverstripe/silverstripe-subsites/commit/73f3d15bfb90ba779dd5498fcc5ae4ab292d6272
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/subsites/CVE-2022-42949.yaml
- https://github.com/silverstripe/silverstripe-subsites
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/cve-2022-42949
