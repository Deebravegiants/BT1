# [M] luci-app-banip Log Monitor IP Extraction Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-62184
Aliases: GHSA-r6hx-4f83-vp8m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62184
Type: osv

## Details
luci-app-banip contains a log parsing vulnerability where the awk-based parser extracts the first IPv4 address from log lines regardless of field position, allowing attackers to inject arbitrary IPs via attacker-controlled fields like usernames. An unauthenticated remote attacker can inject an IP address into the login username field, causing banIP to block the wrong target while the real attacker remains unblocked.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62184.json
- https://github.com/openwrt/luci/security/advisories/GHSA-r6hx-4f83-vp8m
- https://nvd.nist.gov/vuln/detail/CVE-2026-62184
- https://www.vulncheck.com/advisories/luci-app-banip-log-monitor-ip-extraction-bypass
- https://github.com/openwrt/luci/commit/d9bbc372e29618a8807b693a1ccf6d0e42cd196c
- https://github.com/openwrt/luci
