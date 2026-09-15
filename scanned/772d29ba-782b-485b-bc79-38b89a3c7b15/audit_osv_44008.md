# [M] CVE-2026-77639

## Summary
Severity: Medium
Advisory: CVE-2026-77639
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-77639
Type: osv

## Details
Tor before 0.4.9.9 was prone to a compression bomb bypass where an attacker could concatenate many gzip or zlib sub-streams, each just under the per-stream detection threshold, to avoid the compression bomb check entirely. This is TROVE-2026-022.

## References
- https://gitlab.torproject.org/tpo/core/tor/-/raw/tor-0.4.9.9/ChangeLog
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77639.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-77639
