# [C] OpenClaw < 2026.5.22 Untrusted Plugin Loading via Setup-mode

## Summary
Severity: Critical
Advisory: CVE-2026-62222
Aliases: GHSA-rh6r-vvfc-86jq
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62222
Type: osv

## Details
OpenClaw before 2026.5.22 contain a vulnerability in setup-mode discovery that allows loading of untrusted workspace plugins. Attackers with lower-trust caller access or control over configured input paths can execute or persist actions beyond their intended authorization level.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62222.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rh6r-vvfc-86jq
- https://nvd.nist.gov/vuln/detail/CVE-2026-62222
- https://www.vulncheck.com/advisories/openclaw-untrusted-plugin-loading-via-setup-mode
- https://github.com/openclaw/openclaw
