# [C] luci-app-travelmate - Arbitrary Command Execution via UCI Script Parameter

## Summary
Severity: Critical
Advisory: CVE-2026-58652
Aliases: GHSA-p35r-3323-6g7g
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-58652
Type: osv

## Details
luci-app-travelmate (and the travelmate package) contain a privilege-escalation flaw: a LuCI/rpcd session holding the luci-app-travelmate write ACL is granted config-wide UCI write access to the travelmate configuration. While the LuCI UI restricts the auto-login script picker to /etc/travelmate/*.login, this is only a frontend restriction. The backend travelmate service (running as root) reads the raw UCI 'script' and 'script_args' values and executes the configured path when the captive-portal auto-login branch (f_check() in travelmate-functions.sh) is reached. An attacker with delegated write permissions can set script to /bin/sh and script_args to attacker-controlled arguments, resulting in arbitrary command execution as root. Confirmed in luci-app-travelmate/travelmate 2.4.5-r3; the sink is still present in travelmate 2.4.6-1 and no patched version is known.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58652.json
- https://github.com/openwrt/luci/security/advisories/GHSA-p35r-3323-6g7g
- https://nvd.nist.gov/vuln/detail/CVE-2026-58652
- https://www.vulncheck.com/advisories/luci-app-travelmate-arbitrary-command-execution-via-uci-script-parameter
- https://github.com/openwrt/luci/commit/f85102548ee8325bfd581a0327b210b5f7670829
- https://github.com/openwrt/packages/commit/0627b412ee3a760cc4bca9fc8a5b73de8f33ac10
- https://github.com/openwrt/packages/commit/491f1df06645c4e0757fed4a9f0622e9ce0d300c
- https://github.com/openwrt/packages/commit/71d92bcc9edbc8f95858ce82a8ff5d52500005a2
- https://github.com/openwrt/packages/commit/d6e457a1a70a9010195edeafdc0b8eb6e3b0f7f1
