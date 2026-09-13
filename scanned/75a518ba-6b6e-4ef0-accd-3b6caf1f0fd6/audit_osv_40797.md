# [M] OpenWrt: EAD Integer Underflow → Pre-Auth Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-55490
Aliases: GHSA-9558-77jp-g3fw
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-55490
Type: osv

## Details
OpenWrt is a Linux operating system targeting embedded devices. Before v25.12.5, an integer underflow in handle_send_a() of the Emergency Access Daemon allows any unauthenticated attacker on the local network to crash the daemon by sending a single crafted UDP packet. The message length underflows before a bounds check and is then passed to memcpy as a very large size. This issue is fixed v25.12.5.

## References
- https://github.com/openwrt/openwrt/releases/tag/v25.12.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55490.json
- https://github.com/openwrt/openwrt/security/advisories/GHSA-9558-77jp-g3fw
- https://nvd.nist.gov/vuln/detail/CVE-2026-55490
- https://github.com/openwrt/openwrt/commit/63c0767f3d02f7b10b0f0b5293366bd059a08ca5
