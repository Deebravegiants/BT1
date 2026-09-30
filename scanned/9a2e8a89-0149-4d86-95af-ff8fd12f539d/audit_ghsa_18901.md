# [H] Bugsink is vulnerable to unauthenticated remote DoS via crafted Brotli input

## Summary
Severity: High
Advisory: GHSA-fc2v-vcwj-269v
CVE: CVE-2025-64508
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-13
Source: https://github.com/advisories/GHSA-fc2v-vcwj-269v
Type: github-advisory

## Affected
- PyPI: `bugsink` — affected >=0 <2.0.5

## Details
### Impact

In affected versions, brotli "bombs" (highly compressed brotli streams, such as many zeros) can be sent to the server. Since the server will attempt to decompress these streams before applying various maximums, this can lead to exhaustion of the available memory and thus a Denial of Service.

This can be done if the `DSN` is known, which it is in many common setups (JavaScript, Mobile Apps).

### Patches

Patched in Bugsink `2.0.5`

## References
- https://github.com/bugsink/bugsink/security/advisories/GHSA-fc2v-vcwj-269v
- https://nvd.nist.gov/vuln/detail/CVE-2025-64508
- https://github.com/google/brotli/issues/1327
- https://github.com/google/brotli/issues/1375
- https://github.com/bugsink/bugsink/pull/266
- https://github.com/google/brotli/pull/1234
- https://github.com/bugsink/bugsink/commit/3f65544aab3ad5303d97009136640de97b0676a5
- https://github.com/google/brotli/commit/67d78bc41db1a0d03f2e763497748f2f69946627
- https://github.com/bugsink/bugsink
- https://github.com/google/brotli/releases/tag/v1.2.0
