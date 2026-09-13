# [C] luci-proto-openvpn - Command Injection via cl_meta Parameter in generateKey

## Summary
Severity: Critical
Advisory: CVE-2026-58000
Aliases: GHSA-pm9w-522m-8rrh
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-58000
Type: osv

## Details
luci-proto-openvpn through 0.11.1, fixed in commit e4ff45e, contains a command injection vulnerability in the generateKey ubus method where the cl_meta parameter is interpolated into a shell command without proper escaping or quoting. An authenticated LuCI user with OpenVPN protocol configuration access can inject arbitrary shell metacharacters into cl_meta to execute commands as root via the popen function.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58000.json
- https://github.com/openwrt/luci/security/advisories/GHSA-pm9w-522m-8rrh
- https://nvd.nist.gov/vuln/detail/CVE-2026-58000
- https://www.vulncheck.com/advisories/luci-proto-openvpn-command-injection-via-cl-meta-parameter-in-generatekey
- https://github.com/openwrt/luci/commit/e4ff45ecbc6ad212951815c8c99b2749fbd7de6b
- https://github.com/openwrt/luci
