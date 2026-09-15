# [H] aliyundrive-webdav vulnerable to Command Injection

## Summary
Severity: High
Advisory: GHSA-73v2-rxqp-7q4f
CVE: CVE-2024-29640
CWE: CWE-77
Ecosystem: PyPI, crates.io
Published: 2024-03-29
Source: https://github.com/advisories/GHSA-73v2-rxqp-7q4f
Type: github-advisory

## Affected
- crates.io: `aliyundrive-webdav` — affected >=0
- PyPI: `aliyundrive-webdav` — affected >=0

## Details
An issue in aliyundrive-webdav v.2.3.3 and before allows a remote attacker to execute arbitrary code via a crafted payload to the sid parameter in the `action_query_qrcode` component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29640
- https://github.com/lakemoon602/vuln/blob/main/detail.md
- https://github.com/messense/aliyundrive-webdav
- https://github.com/messense/aliyundrive-webdav/blob/main/openwrt/luci-app-aliyundrive-webdav/luasrc/controller/aliyundrive-webdav.lua
- http://aliyundrive-webdav.com
