# [M] Cockpit is vulnerable to directory traversal

## Summary
Severity: Medium
Advisory: GHSA-p46p-7pmj-m34f
CVE: CVE-2026-38993
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-p46p-7pmj-m34f
Type: github-advisory

## Affected
- Packagist: `cockpit-hq/cockpit` — affected >=0 <2.14.0

## Details
Cockpit 2.13.5 and earlier is vulnerable to directory traversal via the Buckets component. This vulnerability allows authenticated attackers to write files to arbitrary locations within the uploads directory or overwrite assets with malicious versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-38993
- https://felsec.com/posts/cockpit-cms-2.13.5-multi-vulns
- https://github.com/Cockpit-HQ/Cockpit
- https://github.com/Cockpit-HQ/Cockpit/releases/tag/2.14.0
