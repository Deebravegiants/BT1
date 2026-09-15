# [M] WCOW cache mount source selector resolves NTFS junctions outside of cache root

## Summary
Severity: Medium
Advisory: CVE-2026-15788
Aliases: GHSA-388v-wmr2-g2v2
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-15788
Type: osv

## Details
BuildKit's cache mount source= selector on Windows Container on Windows (WCOW) workers does not detect NTFS directory junctions placed inside the cache root. A build authored by an untrusted user on a WCOW-configured BuildKit daemon can read arbitrary host files reachable to the BuildKit daemon process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15788.json
- https://github.com/moby/buildkit/security/advisories/GHSA-388v-wmr2-g2v2
- https://nvd.nist.gov/vuln/detail/CVE-2026-15788
