# [H] OpenClaw replaced a deprecated sandbox hash algorithm

## Summary
Severity: High
Advisory: GHSA-fh3f-q9qw-93j9
CVE: CVE-2026-28479
CWE: CWE-327, CWE-328
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-fh3f-q9qw-93j9
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.15

## Details
## Affected Packages / Versions
- npm package: `openclaw`
- Affected versions: `<= 2026.2.14`
- Fixed version (pre-set): `2026.2.15`

## Description
The sandbox identifier cache key for Docker/browser sandbox configuration used SHA-1 to hash normalized configuration payloads.

SHA-1 is deprecated for cryptographic use and has known collision weaknesses. In this code path, deterministic IDs are used to decide whether an existing sandbox container can be reused safely. A collision in this hash could let one configuration be interpreted as another under the same sandbox cache identity, increasing the risk of cache poisoning and unsafe sandbox state reuse.

The implementation now uses SHA-256 for these deterministic hashes to restore collision resistance for this security-relevant identifier path.

## Fix Commit(s)
- `559c8d993`

## Release Process Note
`patched_versions` is pre-set to `2026.2.15` for the next release. After that release is published, mark this advisory ready for publication.

Thanks @kexinoh ( of Tencent zhuque Lab, by https://github.com/Tencent/AI-Infra-Guard) for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-fh3f-q9qw-93j9
- https://nvd.nist.gov/vuln/detail/CVE-2026-28479
- https://github.com/openclaw/openclaw/commit/559c8d9930eebb5356506ff1a8cd3dbaec92be77
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.15
- https://www.vulncheck.com/advisories/openclaw-cache-poisoning-via-deprecated-sha-hash-in-sandbox-configuration
