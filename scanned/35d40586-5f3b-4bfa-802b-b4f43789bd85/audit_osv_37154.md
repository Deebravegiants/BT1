# [C] Arbitrary internal service access via /v1/sys/proxy when Cloudflare Tunnel is enabled on ZimaOS

## Summary
Severity: Critical
Advisory: CVE-2026-28798
Aliases: GHSA-vqqj-f979-8c8m
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-28798
Type: osv

## Details
ZimaOS is a fork of CasaOS, an operating system for Zima devices and x86-64 systems with UEFI. Prior to version 1.5.3, a proxy endpoint (/v1/sys/proxy) exposed by ZimaOS's web interface can be abused (via an externally reachable domain using a Cloudflare Tunnel) to make requests to internal localhost services. This results in unauthenticated access to internal-only endpoints and sensitive local services when the product is reachable from the Internet through a Cloudflare Tunnel. This issue has been patched in version 1.5.3.

## References
- https://github.com/IceWhaleTech/ZimaOS/releases/tag/1.5.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28798.json
- https://github.com/IceWhaleTech/ZimaOS/security/advisories/GHSA-vqqj-f979-8c8m
- https://nvd.nist.gov/vuln/detail/CVE-2026-28798
