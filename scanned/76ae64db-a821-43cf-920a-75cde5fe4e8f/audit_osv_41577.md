# [C] OpenClaw 2026.1.20 < 2026.5.27 Authorization Bypass via device.pair.approve

## Summary
Severity: Critical
Advisory: CVE-2026-62218
Aliases: GHSA-8v95-qqcm-qp9h
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62218
Type: osv

## Details
OpenClaw 2026.1.20 before 2026.5.27 contain an authorization bypass vulnerability in the device.pair.approve feature that allows lower-trust callers to bypass role-management checks. Attackers can perform actions requiring stronger authorization by reaching the affected feature through configured input paths.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62218.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8v95-qqcm-qp9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-62218
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-device-pair-approve
- https://github.com/openclaw/openclaw
