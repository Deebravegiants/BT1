# [M] OpenWrt: ACL bypass and arbitrary root file read via cgi-io cgi-download

## Summary
Severity: Medium
Advisory: CVE-2026-62947
Aliases: GHSA-jw5r-xhf5-2xcq
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-62947
Type: osv

## Details
OpenWrt is a Linux operating system targeting embedded devices. Prior to 25.12.5, the cgi-download handler in cgi-io authorizes the requested path against the caller's ubus session file ACL before canonicalization, and rpcd session.c uses fnmatch() without FNM_PATHNAME, allowing traversal such as an allowed wildcard prefix followed by ../ to read root-readable files including /etc/shadow. This vulnerability is fixed in 25.12.5.

## References
- https://github.com/openwrt/openwrt/releases/tag/v25.12.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62947.json
- https://github.com/openwrt/openwrt/security/advisories/GHSA-jw5r-xhf5-2xcq
- https://nvd.nist.gov/vuln/detail/CVE-2026-62947
- https://github.com/openwrt/cgi-io/commit/72990b7489872112df31c94032637c907760bae4
- https://github.com/openwrt/cgi-io/pull/4
