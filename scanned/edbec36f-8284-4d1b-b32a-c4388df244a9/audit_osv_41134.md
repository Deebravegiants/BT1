# [C] luci-app-tailscale-community - Command Injection via tailscale.do_login RPC

## Summary
Severity: Critical
Advisory: CVE-2026-57999
Aliases: GHSA-xwc5-mx58-rh35
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-57999
Type: osv

## Details
luci-app-tailscale-community contains a command injection vulnerability in the tailscale.do_login RPC method that allows authenticated users to execute arbitrary commands as root. The vulnerability exists because user-controlled loginserver and loginserver_authkey parameters are improperly quoted within a double-quoted shell command, allowing shell substitutions like $() to be evaluated by the outer shell before argument processing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57999.json
- https://github.com/openwrt/luci/security/advisories/GHSA-xwc5-mx58-rh35
- https://nvd.nist.gov/vuln/detail/CVE-2026-57999
- https://www.vulncheck.com/advisories/luci-app-tailscale-community-command-injection-via-tailscale-do-login-rpc
- https://github.com/openwrt/luci
