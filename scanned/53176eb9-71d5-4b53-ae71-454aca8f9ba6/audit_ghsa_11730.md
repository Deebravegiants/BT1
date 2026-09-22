# [H] act: actions/cache server allows malicious cache injection

## Summary
Severity: High
Advisory: GHSA-x34h-54cw-9825
CVE: CVE-2026-34042
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-x34h-54cw-9825
Type: github-advisory

## Affected
- Go: `github.com/nektos/act` — affected >=0 <0.2.86

## Details
act's built-in actions/cache server listens to connections on all interfaces and allows anyone who can connect to it — including someone anywhere on the internet — to create caches with arbitrary keys and retrieve all existing caches. If one can predict which cache keys will be used by local actions, one can create malicious caches containing whatever files one pleases, most likely allowing arbitrary remote code execution within the Docker container.

## Discovery

Discovered while discussing [forgejo/runner#294](https://code.forgejo.org/forgejo/runner/issues/294).

## Proposed Mitigation

It was discussed to append a secret to `ACTIONS_CACHE_URL` to retain compatibility with GitHub's cache action and still allow authorization. Forgejo is considering also encoding which repo is currently being run in CI into the secret in the URL to prevent unrelated repos using the same (probably global) runner from seeing each other's caches.

## References
- https://github.com/nektos/act/security/advisories/GHSA-x34h-54cw-9825
- https://nvd.nist.gov/vuln/detail/CVE-2026-34042
- https://github.com/nektos/act/commit/c28c27e141e8b54f9853de82f421ee09846751f7
- https://code.forgejo.org/forgejo/runner/issues/294
- https://github.com/nektos/act
- https://github.com/nektos/act/releases/tag/v0.2.86
