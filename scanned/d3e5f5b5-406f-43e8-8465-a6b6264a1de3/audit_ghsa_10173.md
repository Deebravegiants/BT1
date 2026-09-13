# [H] @mobilenext/mobile-mcp: Arbitrary Android Intent Execution via mobile_open_url

## Summary
Severity: High
Advisory: GHSA-5qhv-x9j4-c3vm
CVE: CVE-2026-35394
CWE: CWE-939
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-5qhv-x9j4-c3vm
Type: github-advisory

## Affected
- npm: `@mobilenext/mobile-mcp` — affected >=0 <0.0.50

## Details
### Summary

The `mobile_open_url` tool in mobile-mcp passes user-supplied URLs directly to Android's intent system without any scheme validation, allowing execution of arbitrary Android intents, including USSD codes, phone calls, SMS messages, and content provider access.

### Details

The vulnerable code passes URLs directly to `adb shell am start -a android.intent.action.VIEW -d <url>` without checking the URL scheme. This can enable malicious schemes such as `tel:`, `sms:`, `mailto:`, `content://`, and `market://` to be executed.

Since MCP servers are designed to be operated by AI agents, which are vulnerable to prompt injection attacks, a malicious document or website could inject instructions that cause the AI to execute dangerous intents on a connected mobile device.

### Impact

An attacker via prompt injection can:
- Execute USSD codes (e.g., `tel:*#06#` to display IMEI - confirmed on Pixel 7a, behavior varies by device; or device-specific factory reset codes)
- Initiate phone calls to premium rate numbers
- Draft SMS messages with attacker-controlled content
- Access content providers (contacts, SMS, call logs)
- Open app installation prompts

### Proof of Concept
```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"mobile_open_url","arguments":{"device":"<id>","url":"tel:*#06#"}}}
```

Result: IMEI displayed on device.
```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"mobile_open_url","arguments":{"device":"<id>","url":"sms:1234567890?body=HACKED"}}}
```

Result: SMS app opens with a pre-filled message.

### Remediation

Upgrade to version 0.0.50 or later, which restricts `mobile_open_url` to `http://` and `https://` schemes by default. Users who require other URL schemes can opt in by setting `MOBILEMCP_ALLOW_UNSAFE_URLS=1`.

## References
- https://github.com/mobile-next/mobile-mcp/security/advisories/GHSA-5qhv-x9j4-c3vm
- https://nvd.nist.gov/vuln/detail/CVE-2026-35394
- https://github.com/mobile-next/mobile-mcp/pull/299
- https://github.com/mobile-next/mobile-mcp
- https://github.com/mobile-next/mobile-mcp/releases/tag/0.0.50
