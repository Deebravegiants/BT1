# [M] OpenClaw has ReDoS and regex injection via unescaped Feishu mention metadata in RegExp construction

## Summary
Severity: Medium
Advisory: GHSA-c6hr-w26q-c636
CVE: CVE-2026-22178
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-c6hr-w26q-c636
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
## Summary

`extensions/feishu/src/bot.ts` constructed `new RegExp()` directly from Feishu mention metadata (`mention.name`, `mention.key`) in `stripBotMention()` without escaping regex metacharacters.

## Affected Packages / Versions

- Package: npm `openclaw`
- Affected versions: `<= 2026.2.17`
- First affected release: `2026.2.6`
- Patched version: `2026.2.19`

## Impact

- ReDoS: crafted nested-quantifier patterns in mention metadata can trigger catastrophic backtracking and block message processing.
- Regex injection: metacharacters in mention metadata can remove unintended message content before it is sent to the model.

## Fix Commit(s)

- `7e67ab75cc2f0e93569d12fecd1411c2961fcc8c`
- `74268489137510b6f6349919d1e197b17290d92c`

Thanks @allsmog for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-c6hr-w26q-c636
- https://nvd.nist.gov/vuln/detail/CVE-2026-22178
- https://github.com/openclaw/openclaw/commit/74268489137510b6f6349919d1e197b17290d92c
- https://github.com/openclaw/openclaw/commit/7e67ab75cc2f0e93569d12fecd1411c2961fcc8c
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-redos-and-regex-injection-via-unescaped-feishu-mention-metadata
