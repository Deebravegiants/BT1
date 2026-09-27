# [M] PlexRipper allows API leak due to open CORS policy

## Summary
Severity: Medium
Advisory: CVE-2024-49763
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-49763
Type: osv

## Details
PlexRipper is a cross-platform media downloader for Plex. PlexRipper’s open CORS policy allows attackers to gain sensitive information from PlexRipper by getting the user to access the attacker’s domain. This allows an attacking website to access the /api/PlexAccount endpoint and steal the user’s Plex login. This vulnerability is fixed in 0.24.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49763.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49763
- https://securitylab.github.com/advisories/GHSL-2024-305_PlexRipper/
- https://github.com/PlexRipper/PlexRipper/commit/184074644a1f5a8ac59519929a9c4b92280fb2a1
