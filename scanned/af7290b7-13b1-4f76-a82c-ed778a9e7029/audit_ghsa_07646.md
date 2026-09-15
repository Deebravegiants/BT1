# [C] OpenClaw has a potential access-group authorization bypass if channel type lookup fails

## Summary
Severity: Critical
Advisory: GHSA-fhvm-j76f-qmjv
CVE: CVE-2026-28454
CWE: CWE-285, CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-fhvm-j76f-qmjv
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.1

## Details
## Summary

When Telegram webhook mode is enabled without a configured webhook secret, OpenClaw may accept unauthenticated HTTP POST requests at the Telegram webhook endpoint and trust attacker-controlled update JSON. This can allow forged Telegram updates that spoof `message.from.id` / `chat.id`, potentially bypassing sender allowlists and executing privileged bot commands.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<= 2026.1.30`
- Patched: `>= 2026.2.1`

## Impact

An attacker who can reach the webhook endpoint can forge Telegram updates and impersonate allowlisted/paired senders by spoofing fields in the webhook payload (for example `message.from.id`). Impact depends on enabled commands/tools and the deployment’s network exposure.

## Mitigations / Workarounds

- Configure a strong `channels.telegram.webhookSecret` and ensure your reverse proxy forwards the `X-Telegram-Bot-Api-Secret-Token` header unchanged.

## Fix Commit(s)

- ca92597e1f9593236ad86810b66633144b69314d (config validation: `webhookUrl` requires `webhookSecret`)

Defense-in-depth / supporting fixes:

- 5643a934799dc523ec2ef18c007e1aa2c386b670 (default webhook listener bind host to loopback)
- 3cbcba10cf30c2ffb898f0d8c7dfb929f15f8930 (bound webhook request body size/time)
- 633fe8b9c17f02fcc68ecdb5ec212a5ace932f09 (runtime guard: reject webhook startup when secret is missing/empty)

## Release Process Note

`patched_versions` is set to the first fixed release (`2026.2.1`).

Thanks @yueyueL for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-fhvm-j76f-qmjv
- https://nvd.nist.gov/vuln/detail/CVE-2026-28454
- https://github.com/openclaw/openclaw/commit/3cbcba10cf30c2ffb898f0d8c7dfb929f15f8930
- https://github.com/openclaw/openclaw/commit/5643a934799dc523ec2ef18c007e1aa2c386b670
- https://github.com/openclaw/openclaw/commit/633fe8b9c17f02fcc68ecdb5ec212a5ace932f09
- https://github.com/openclaw/openclaw/commit/ca92597e1f9593236ad86810b66633144b69314d
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.1
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-unauthenticated-telegram-webhook
