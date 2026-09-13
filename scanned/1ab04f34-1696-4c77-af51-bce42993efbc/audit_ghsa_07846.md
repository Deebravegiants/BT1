# [H] OpenClaw has a Telegram webhook request forgery (missing `channels.telegram.webhookSecret`) → auth bypass

## Summary
Severity: High
Advisory: GHSA-mp5h-m6qj-6292
CVE: CVE-2026-25474
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-mp5h-m6qj-6292
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.1

## Details
## Summary

In Telegram webhook mode, if `channels.telegram.webhookSecret` is not set, OpenClaw may accept webhook HTTP requests without verifying Telegram’s secret token header. In deployments where the webhook endpoint is reachable by an attacker, this can allow forged Telegram updates (for example spoofing `message.from.id`).

Note: Telegram webhook mode is not enabled by default. It is enabled only when `channels.telegram.webhookUrl` is configured.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<= 2026.1.30`
- Patched: `>= 2026.2.1`

## Impact

If an attacker can reach the webhook endpoint, they may be able to send forged updates that are processed as if they came from Telegram. Depending on enabled commands/tools and configuration, this could lead to unintended bot actions.

## Mitigations / Workarounds

- Set a strong `channels.telegram.webhookSecret` and ensure your reverse proxy forwards the `X-Telegram-Bot-Api-Secret-Token` header unchanged.
- Restrict network access to the webhook endpoint (for example bind to loopback and only expose via a reverse proxy).

## Fix Commit(s)

- ca92597e1f9593236ad86810b66633144b69314d (config validation: `webhookUrl` requires `webhookSecret`)

Defense-in-depth / supporting fixes:

- 5643a934799dc523ec2ef18c007e1aa2c386b670 (default webhook listener bind host to loopback)
- 3cbcba10cf30c2ffb898f0d8c7dfb929f15f8930 (bound webhook request body size/time)
- 633fe8b9c17f02fcc68ecdb5ec212a5ace932f09 (runtime guard: reject webhook startup when secret is missing/empty)

Thanks @yueyueL for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mp5h-m6qj-6292
- https://nvd.nist.gov/vuln/detail/CVE-2026-25474
- https://github.com/openclaw/openclaw/commit/3cbcba10cf30c2ffb898f0d8c7dfb929f15f8930
- https://github.com/openclaw/openclaw/commit/5643a934799dc523ec2ef18c007e1aa2c386b670
- https://github.com/openclaw/openclaw/commit/633fe8b9c17f02fcc68ecdb5ec212a5ace932f09
- https://github.com/openclaw/openclaw/commit/ca92597e1f9593236ad86810b66633144b69314d
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.1
