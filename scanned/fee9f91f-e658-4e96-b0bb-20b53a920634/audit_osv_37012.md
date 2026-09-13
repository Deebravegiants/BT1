# [M] Homarr: Unauthenticated SSRF in rssFeed.ts

## Summary
Severity: Medium
Advisory: CVE-2026-27797
Aliases: GHSA-vwqf-2f4m-2cq2
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-07
Source: https://osv.dev/vulnerability/CVE-2026-27797
Type: osv

## Details
Homarr is an open-source dashboard. Prior to version 1.54.0, an unauthenticated Server-Side Request Forgery (SSRF) vulnerability allows a remote attacker to force the Homarr server to perform arbitrary outbound HTTP requests. This can be used as an internal network access primitive (e.g., reaching loopback/private ranges) from the Homarr host/container network context. This issue has been patched in version 1.54.0.

## References
- https://github.com/homarr-labs/homarr/releases/tag/v1.54.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27797.json
- https://github.com/homarr-labs/homarr/security/advisories/GHSA-vwqf-2f4m-2cq2
- https://nvd.nist.gov/vuln/detail/CVE-2026-27797
- https://github.com/homarr-labs/homarr/commit/fce970c70653f200ff1c73081139a77f0379bd91
