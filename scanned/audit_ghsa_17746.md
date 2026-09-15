# [M] DevDojo Voyager Arbitrary File Write

## Summary
Severity: Medium
Advisory: GHSA-35p2-5vrh-m3p6
CVE: CVE-2024-55417
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-01-30
Source: https://github.com/advisories/GHSA-35p2-5vrh-m3p6
Type: github-advisory

## Affected
- Packagist: `tcg/voyager` — affected >=0

## Details
DevDojo Voyager through version 1.8.0 is vulnerable to bypassing the file type verification when an authenticated user uploads a file via /admin/media/upload. An authenticated user can upload a web shell causing arbitrary code execution on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-55417
- https://github.com/thedevdojo/voyager
- https://github.com/thedevdojo/voyager/blob/1.6/src/Http/Controllers/VoyagerMediaController.php#L238
- https://www.sonarsource.com/blog/the-tainted-voyage-uncovering-voyagers-vulnerabilities
