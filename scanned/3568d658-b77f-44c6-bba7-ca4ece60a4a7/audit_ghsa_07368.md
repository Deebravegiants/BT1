# [M] Pion DTLS vulnerable to denial of service via panic while parsing a crafted ECDHE_PSK ServerKeyExchange message

## Summary
Severity: Medium
Advisory: GHSA-wg4g-wm44-ch5j
CVE: CVE-2026-54908
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-wg4g-wm44-ch5j
Type: github-advisory

## Affected
- Go: `github.com/pion/dtls/v3` — affected >=0 <3.1.4

## Details
### Impact
Remote denial of service via panic while parsing a crafted ECDHE_PSK ServerKeyExchange message.

### Patches
Upgrade to v3.1.4 or later. This version includes this patch https://github.com/pion/dtls/pull/839 which fixes the issue.

### Workarounds
No work around; please upgrade to v3.1.4 or a newer version.

## References
- https://github.com/pion/dtls/security/advisories/GHSA-wg4g-wm44-ch5j
- https://nvd.nist.gov/vuln/detail/CVE-2026-54908
- https://github.com/pion/dtls/pull/839
- https://github.com/pion/dtls/commit/49458d604a4f3ebce1bf9587a0f3e5f3f6b4a55e
- https://github.com/pion/dtls
- https://github.com/pion/dtls/releases/tag/v3.1.3
