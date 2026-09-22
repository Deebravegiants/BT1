# [H] smtp-server's command parser memory exhaustion denial-of-service

## Summary
Severity: High
Advisory: GHSA-fv2f-rw9f-v9cm
CVE: CVE-2026-38728
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-fv2f-rw9f-v9cm
Type: github-advisory

## Affected
- npm: `smtp-server` — affected >=0 <3.18.3

## Details
smtp-server prior to v3.18.3 are vulnerable to unauthenticated memory exhaustion denial-of-service. smtp-server's command parser allows any remote client to consume server memory by sending data without newline characters. The server's `_remainder` buffer in `SMTPStream._write` grows without limit, leading to heap exhaustion, prolonged GC pauses that freeze the event loop, and in some cases, process crash.

The `_write` method in `lib/smtp-stream.js` appends incoming TCP chunks to `this._remainder` in command mode. The buffer is only emptied when a newline is found. If a client never sends a newline, the `_remainder` value will grow indefinitely, causing excess memory consumption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-38728
- https://github.com/nodemailer/smtp-server/commit/592c5666fa0c76d1d04c1a32abad0ef806fbfe97
- https://bytecreator.dev/blog/CVE-2026-38728
- https://github.com/nodemailer/smtp-server
- https://github.com/nodemailer/smtp-server/releases/tag/v3.18.3
