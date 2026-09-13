# [C] Vibe-Trading < 0.1.10 - Loopback Trust and Missing Host Validation Enable DNS-Rebinding Authentication Bypass and Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-58169
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58169
Type: osv

## Details
Vibe-Trading before 0.1.10 contains a DNS rebinding authentication bypass vulnerability that allows remote attackers to bypass bearer-token authentication by exploiting the server's trust of TCP peer addresses for loopback clients combined with missing Host header validation while binding to 0.0.0.0 with credentialed CORS. Attackers can craft a malicious DNS rebinding page to issue authenticated requests to the local API server, reach the shell execution endpoint with a bash-enabled preset, and achieve remote code execution as the API process user while also overwriting LLM and data-source settings to exfiltrate credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58169.json
- https://github.com/HKUDS/Vibe-Trading/releases/tag/v0.1.10
- https://nvd.nist.gov/vuln/detail/CVE-2026-58169
- https://www.vulncheck.com/advisories/vibe-trading-loopback-trust-and-missing-host-validation-enable-dns-rebinding-authentication-bypass-and-remote-code-execution
- https://github.com/HKUDS/Vibe-Trading/pull/241
- https://github.com/HKUDS/Vibe-Trading/pull/242
- https://github.com/HKUDS/Vibe-Trading/pull/243
- https://github.com/HKUDS/Vibe-Trading/pull/245
- https://github.com/HKUDS/Vibe-Trading/pull/293
- https://github.com/HKUDS/Vibe-Trading
