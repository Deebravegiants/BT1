# [M] OpenClaw improperly parses X-Forwarded-For behind trusted proxies allows client IP spoofing in security decisions

## Summary
Severity: Medium
Advisory: GHSA-2rgf-hm63-5qph
CVE: CVE-2026-32029
CWE: CWE-345, CWE-807
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-2rgf-hm63-5qph
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
### Summary

OpenClaw used left-most `X-Forwarded-For` values when requests came from configured trusted proxies. In proxy chains that append/preserve header values, this could let attacker-controlled header content influence security decisions tied to client IP.

### Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<= 2026.2.19-2`
- Patched: `2026.2.21` (planned next release)

### Impact

Possible client-IP spoofing in security-sensitive paths (for example auth rate-limit identity and local/private classification) for deployments behind trusted proxies with non-recommended forwarding behavior.

### Scope Note

OpenClaw docs recommend reverse proxies overwrite (not append/preserve) inbound forwarding headers. This condition reduces severity.

### Fix Commit(s)

- `07039dc089e51589a213ec0d16f8d6f2cd871fa1`
- `8877bfd11ec7760b115b2d0d7500a45da2749747`

### Release Process Note

`patched_versions` is pre-set to the planned next release (`2026.2.21`). After npm release is out, publish this advisory.

OpenClaw thanks @AnthonyDiSanti for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2rgf-hm63-5qph
- https://nvd.nist.gov/vuln/detail/CVE-2026-32029
- https://github.com/openclaw/openclaw/commit/07039dc089e51589a213ec0d16f8d6f2cd871fa1
- https://github.com/openclaw/openclaw/commit/8877bfd11ec7760b115b2d0d7500a45da2749747
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-client-ip-spoofing-via-x-forwarded-for-header-parsing
