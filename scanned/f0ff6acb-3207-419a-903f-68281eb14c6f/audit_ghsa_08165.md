# [M] OpenClaw: Telegram bot token exposure via logs

## Summary
Severity: Medium
Advisory: GHSA-chf7-jq6g-qrwv
CVE: CVE-2026-27003
CWE: CWE-522
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-chf7-jq6g-qrwv
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.15

## Details
## Vulnerability

Telegram bot tokens can appear in error messages and stack traces (for example, when request URLs include `https://api.telegram.org/bot<token>/...`). OpenClaw previously logged these strings without redaction, which could leak the bot token into logs, crash reports, CI output, or support bundles.

## Impact

Disclosure of a Telegram bot token allows an attacker to impersonate the bot and take over Bot API access.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<= 2026.2.14`
- Fixed: `>= 2026.2.15` (next release)

## Mitigation

- Upgrade to `openclaw >= 2026.2.15` when released.
- Rotate the Telegram bot token if it may have been exposed.

## Fix Commit(s)

- cf6990701b258bb9cc4ac7f6c7bdf05016e7f6e46

Thanks @aether-ai-agent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-chf7-jq6g-qrwv
- https://nvd.nist.gov/vuln/detail/CVE-2026-27003
- https://github.com/openclaw/openclaw/commit/cf69907015b659e5025efb735ee31bd05c4ee3d5
- https://github.com/openclaw/openclaw
