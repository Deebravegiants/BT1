# [M] Avahi has a reachable assertion in avahi_wide_area_scan_cache

## Summary
Severity: Medium
Advisory: CVE-2025-68276
Aliases: GHSA-mhf3-865v-g5rc
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2025-68276
Type: osv

## Details
Avahi is a system which facilitates service discovery on a local network via the mDNS/DNS-SD protocol suite. In 0.9-rc2 and earlier, an unprivileged local users can crash avahi-daemon (with wide-area disabled) by creating record browsers with the AVAHI_LOOKUP_USE_WIDE_AREA flag set via D-Bus. This can be done by either calling
the RecordBrowserNew method directly or creating hostname/address/service resolvers/browsers that create those browsers internally themselves.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68276.json
- https://github.com/avahi/avahi/security/advisories/GHSA-mhf3-865v-g5rc
- https://nvd.nist.gov/vuln/detail/CVE-2025-68276
- https://github.com/avahi/avahi/commit/ede7048475c5d47d53890e3bc1350dda8e0b3688
- https://github.com/avahi/avahi/pull/806
