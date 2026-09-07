# [M] OpenClaw: denial of service through large base64 media files allocating large buffers before limit checks

## Summary
Severity: Medium
Advisory: GHSA-w2cg-vxx6-5xjg
CVE: CVE-2026-29612
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-w2cg-vxx6-5xjg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14
- npm: `clawdbot` — affected >=0

## Details
## Summary

Base64-backed media inputs could be decoded into Buffers before enforcing decoded-size budgets. An attacker supplying oversized base64 payloads can force large allocations, causing memory pressure and denial of service.

## Attack Scenario Notes

- Recommended deployments bind the gateway to loopback by default and require gateway auth for HTTP endpoints. In that configuration, this is best modeled as a local/authorized DoS.
- If an operator exposes the gateway to untrusted networks (or disables/weakens auth and rate limits), treat this as a higher-severity network DoS risk.

## Affected Packages / Versions

- openclaw (npm): <= 2026.2.13
- clawdbot (npm): <= 2026.1.24-3

## Fixed In

- openclaw (npm): 2026.2.14 (planned)
- clawdbot (npm): no patched release planned; migrate to openclaw

## Fix Commit(s)

- 31791233d60495725fa012745dde8d6ee69e9595

## Credits
Thanks @vincentkoc for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w2cg-vxx6-5xjg
- https://nvd.nist.gov/vuln/detail/CVE-2026-29612
- https://github.com/openclaw/openclaw/commit/31791233d60495725fa012745dde8d6ee69e9595
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
- https://www.vulncheck.com/advisories/openclaw-denial-of-service-via-large-base-media-file-decoding
