# [M] HKUDS OpenHarness Insecure Default Remote Channel Allowlist

## Summary
Severity: Medium
Advisory: CVE-2026-6823
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-6823
Type: osv

## Details
HKUDS OpenHarness prior to PR #147 remediation contains an insecure default configuration vulnerability where remote channels inherit allow_from = ["*"] permitting arbitrary remote senders to pass admission checks. Attackers who can reach the configured channel can bypass access controls and reach host-backed agent runtimes, potentially leading to unauthorized file disclosure and read access through default-enabled read-only tools.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6823.json
- https://github.com/HKUDS/OpenHarness/releases/tag/v0.1.7
- https://nvd.nist.gov/vuln/detail/CVE-2026-6823
- https://www.vulncheck.com/advisories/hkuds-openharness-insecure-default-remote-channel-allowlist
- https://github.com/HKUDS/OpenHarness/pull/147
- https://github.com/HKUDS/OpenHarness/commit/fab40c6eabfb15f2bdf23cddd3cfe66a64ea203d
