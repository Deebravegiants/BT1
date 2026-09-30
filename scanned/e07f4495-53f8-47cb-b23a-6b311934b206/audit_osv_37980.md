# [M] xdg-dbus-proxy has an eavesdrop filter bypass allowing message interception

## Summary
Severity: Medium
Advisory: CVE-2026-34080
Aliases: GHSA-vjp5-hjfm-7677
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-34080
Type: osv

## Details
xdg-dbus-proxy is a filtering proxy for D-Bus connections. Prior to 0.1.7, a policy parser vulnerability allows bypassing eavesdrop restrictions. The proxy checks for eavesdrop=true in policy rules but fails to handle eavesdrop ='true' (with a space before the equals sign) and similar cases. Clients can intercept D-Bus messages they should not have access to. This vulnerability is fixed in 0.1.7.

## References
- http://www.openwall.com/lists/oss-security/2026/04/10/15
- https://lists.debian.org/debian-lts-announce/2026/04/msg00022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34080.json
- https://github.com/flatpak/xdg-dbus-proxy/security/advisories/GHSA-vjp5-hjfm-7677
- https://nvd.nist.gov/vuln/detail/CVE-2026-34080
