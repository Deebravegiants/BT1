# [M] Grav CMS before 2.0.16 Path Traversal via media_directory

## Summary
Severity: Medium
Advisory: CVE-2026-72697
Aliases: GHSA-47ch-6w46-6xm7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-72697
Type: osv

## Details
Grav CMS before 2.0.16 contains a path traversal vulnerability in the media_directory() Twig function that fails to validate filesystem paths, allowing authenticated users to enumerate and access files outside intended scope. Attackers with page authoring privileges can supply arbitrary filesystem paths to media_directory() and use the allow-listed filepath accessor on Medium objects to read file contents of any file matching configured media extensions that the web server process can access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72697.json
- https://github.com/getgrav/grav/security/advisories/GHSA-47ch-6w46-6xm7
- https://nvd.nist.gov/vuln/detail/CVE-2026-72697
- https://www.vulncheck.com/advisories/grav-cms-before-path-traversal-via-media-directory
