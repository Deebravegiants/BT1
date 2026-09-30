# [M] Kimi Code FetchURL SSRF protection bypass via DNS-resolving hostnames and redirects

## Summary
Severity: Medium
Advisory: CVE-2026-17534
CVSS: 5.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-17534
Type: osv

## Details
Kimi Code (@moonshot-ai/kimi-code) before 0.27.0 implements FetchURL SSRF hardening as a static hostname and IP-literal denylist in assertSafeFetchTarget, without resolving DNS or re-validating hosts after HTTP redirects. An attacker who can influence a FetchURL call (for example via prompt injection) can supply a crafted public hostname that resolves to loopback or another internal address, or a public URL that redirects to such a target, and thereby reach internal network services that the denylist was intended to block. FetchURL is included in the default auto-approve tool set, so the call does not require interactive user confirmation in manual mode.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/17xxx/CVE-2026-17534.json
- https://github.com/MoonshotAI/kimi-code/releases/tag/%40moonshot-ai%2Fkimi-code%400.27.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-17534
- https://github.com/MoonshotAI/kimi-code/commit/31449728b72df94e22bcb2de350a1e7624895e30
- https://github.com/MoonshotAI/kimi-code/pull/1791
- git://github.com/MoonshotAI/kimi-code
- https://github.com/MoonshotAI/kimi-code
