# [M] Sandboxie kernel driver denial of service via malformed IOCTL from sandboxed process

## Summary
Severity: Medium
Advisory: CVE-2026-32603
Aliases: GHSA-vvf8-cf4j-v8fv
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-32603
Type: osv

## Details
Sandboxie is an open source sandbox-based isolation software for Windows. In versions 1.17.2 and earlier, a local denial of service vulnerability exists in the Sandboxie kernel driver. An unprivileged process running inside a Standard Sandbox can send a malformed IOCTL to the \Device\SandboxieDriverApi driver, triggering an immediate kernel crash (BSOD). The vulnerability affects the Standard Sandbox configuration both with and without dropped administrator privileges, but does not affect the Security Hardened Sandbox configuration. This issue has been fixed in version 1.17.3. Users who cannot update can use the Security Hardened Sandbox configuration as a workaround.

## References
- https://github.com/sandboxie-plus/Sandboxie/releases/tag/v1.17.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32603.json
- https://github.com/sandboxie-plus/Sandboxie/security/advisories/GHSA-vvf8-cf4j-v8fv
- https://nvd.nist.gov/vuln/detail/CVE-2026-32603
