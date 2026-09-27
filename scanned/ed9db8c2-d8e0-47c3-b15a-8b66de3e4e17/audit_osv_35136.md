# [M] Avahi has a reachable assertion in lookup_start

## Summary
Severity: Medium
Advisory: CVE-2025-68471
Aliases: GHSA-56rf-42xr-qmmg
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2025-68471
Type: osv

## Details
Avahi is a system which facilitates service discovery on a local network via the mDNS/DNS-SD protocol suite. In 0.9-rc2 and earlier, avahi-daemon can be crashed by sending 2 unsolicited announcements with CNAME resource records 2 seconds apart.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68471.json
- https://github.com/avahi/avahi/security/advisories/GHSA-56rf-42xr-qmmg
- https://nvd.nist.gov/vuln/detail/CVE-2025-68471
- https://github.com/avahi/avahi/issues/678
- https://github.com/avahi/avahi/commit/9c6eb53bf2e290aed84b1f207e3ce35c54cc0aa1
