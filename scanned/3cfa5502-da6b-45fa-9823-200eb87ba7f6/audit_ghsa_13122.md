# [M] Cockpit CMS arbitrary file upload vulnerability

## Summary
Severity: Medium
Advisory: GHSA-38vf-35cg-m73w
CVE: CVE-2023-41564
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-09-09
Source: https://github.com/advisories/GHSA-38vf-35cg-m73w
Type: github-advisory

## Affected
- Packagist: `cockpit-hq/cockpit` — affected >=0

## Details
An arbitrary file upload vulnerability in the Upload Asset function of Cockpit CMS v2.6.3 allows attackers to execute arbitrary code via uploading a crafted `.shtml` file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41564
- https://github.com/Cockpit-HQ/Cockpit
- https://github.com/LongHair00/Mitre_opensource_report/blob/main/CockpitCMS-StoredXSS.md
