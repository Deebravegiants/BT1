# [M] WeKan < 8.19 allowPrivateOnly Setting Enforcement Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-25568
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-07
Source: https://osv.dev/vulnerability/CVE-2026-25568
Type: osv

## Details
WeKan versions prior to 8.19 contain an authorization logic vulnerability where the instance configuration setting allowPrivateOnly is not sufficiently enforced at board creation time. When allowPrivateOnly is enabled, users can still create public boards due to incomplete server-side enforcement.

## References
- https://wekan.fi/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25568.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25568
- https://www.vulncheck.com/advisories/wekan-allowprivateonly-setting-enforcement-bypass
- https://github.com/wekan/wekan/commit/7ed76c180ede46ab1dac6b8ad27e9128a272c2c8
- https://github.com/wekan/wekan
