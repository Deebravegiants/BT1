# [C] luci-app-https-dns-proxy Authenticated Command Injection via setInitAction

## Summary
Severity: Critical
Advisory: CVE-2026-46368
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-46368
Type: osv

## Details
luci-app-https-dns-proxy through 2025.12.29-5 — an optional LuCI web UI add-on for the https-dns-proxy package, distributed through the OpenWrt community packages feed and not installed by default — contains a command injection vulnerability in the setInitAction function. An authenticated user holding the luci.https-dns-proxy ACL permission can inject shell metacharacters through the 'name' parameter of a ubus RPC call to luci.https-dns-proxy setInitAction, resulting in arbitrary command execution as root on the underlying device. Core OpenWrt is not affected; only installations that have opted in to the luci-app-https-dns-proxy package are vulnerable.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46368.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46368
- https://www.vulncheck.com/advisories/luci-app-https-dns-proxy-authenticated-command-injection-via-setinitaction
- https://github.com/stangri/luci-app-https-dns-proxy
- https://www.exploit-db.com/exploits/52521
