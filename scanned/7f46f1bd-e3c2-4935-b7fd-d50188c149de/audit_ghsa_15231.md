# [H] Cross-Frame Scripting vulnerability has been found on Plone CMS

## Summary
Severity: High
Advisory: GHSA-5xfx-55x4-j223
CVE: CVE-2024-0669
CWE: CWE-1021
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-18
Source: https://github.com/advisories/GHSA-5xfx-55x4-j223
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <6.0.7

## Details
A Cross-Frame Scripting vulnerability has been found on Plone CMS affecting version below 6.0.5. An attacker could store a malicious URL to be opened by an administrator and execute a malicios iframe element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-0669
- https://github.com/plone/Plone
- https://www.incibe.es/en/incibe-cert/notices/aviso/cross-frame-scripting-xfs-plone-cms
