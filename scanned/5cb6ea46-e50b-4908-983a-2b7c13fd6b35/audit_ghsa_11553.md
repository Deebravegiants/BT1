# [H] OpenClaw's inbound media downloads could exceed configured byte limits before rejection across multiple channels

## Summary
Severity: High
Advisory: GHSA-rxxp-482v-7mrh
CVE: CVE-2026-32049
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-rxxp-482v-7mrh
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
## Summary
OpenClaw did not consistently enforce configured inbound media byte limits before buffering remote media in several channel ingestion paths. A remote sender could trigger oversized downloads and memory pressure before rejection.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.21-2` (latest published at triage time)
- Fixed in: `2026.2.22` (planned next release)

## Impact
An attacker could cause elevated memory usage and potential process instability (denial of service) by sending oversized media payloads.

## Fix Commit(s)
- `73d93dee64127a26f1acd09d0403b794cdeb4f5c`

## Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.22`). After that npm release is published, this advisory can be published without further version-field edits.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rxxp-482v-7mrh
- https://nvd.nist.gov/vuln/detail/CVE-2026-32049
- https://github.com/openclaw/openclaw/commit/73d93dee64127a26f1acd09d0403b794cdeb4f5c
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-denial-of-service-via-inbound-media-download-byte-limit-bypass
