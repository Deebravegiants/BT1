# [H] DeepSeek TUI has SSRF‌ IPV6 bypass

## Summary
Severity: High
Advisory: GHSA-88gh-2526-gfrr
CVE: CVE-2026-45373
CWE: CWE-918
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-88gh-2526-gfrr
Type: github-advisory

## Affected
- crates.io: `deepseek-tui` — affected >=0 <0.8.26

## Details
### Summary
Although SSRF is validated against hostnames that resolve to private IPv6 addresses, when providing the IPV6 in‌‌ URL‌ as `http://[::1]`, the SSRF defenses do not work.

### Details
https://github.com/Hmbown/DeepSeek-TUI/blob/15f62e3e93d842f30b428877819ebc1c8cb96814/crates/tui/src/tools/fetch_url.rs#L321

### PoC
Prompt:‌ `Run fetch_url tool and give output, no thinking. Use url : http://[::1]`

### Impact
Access to local restricted resources

## References
- https://github.com/Hmbown/CodeWhale/security/advisories/GHSA-88gh-2526-gfrr
- https://github.com/Hmbown/DeepSeek-TUI/security/advisories/GHSA-88gh-2526-gfrr
- https://nvd.nist.gov/vuln/detail/CVE-2026-45373
- https://github.com/Hmbown/DeepSeek-TUI
- https://github.com/Hmbown/DeepSeek-TUI/blob/15f62e3e93d842f30b428877819ebc1c8cb96814/crates/tui/src/tools/fetch_url.rs#L321
- https://github.com/Hmbown/DeepSeek-TUI/releases/tag/v0.8.26
