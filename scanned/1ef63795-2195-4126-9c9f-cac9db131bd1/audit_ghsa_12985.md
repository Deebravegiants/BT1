# [H] Woodpecker does not validate webhook before changing any data

## Summary
Severity: High
Advisory: GHSA-4gcf-5m39-98mc
CVE: CVE-2023-40034
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-16
Source: https://github.com/advisories/GHSA-4gcf-5m39-98mc
Type: github-advisory

## Affected
- Go: `github.com/woodpecker-ci/woodpecker` — affected >=1.0.0 <1.0.2

## Details
### Impact
An attacker can post malformed webhook data which leads to an update of the repository data that can e.g. allow the takeover of a repository.
This is only critical if the CI is configured for public usage and connected to a forge witch is also in public usage.

### Patches
Please use either next or the latest v1.0 e.g. v1.0.2

### Workarounds
Secure the CI system by making it inaccessible to untrusted entities, for example, by placing it behind a firewall.

### References
Fix: https://github.com/woodpecker-ci/woodpecker/pull/2221
Backport: https://github.com/woodpecker-ci/woodpecker/pull/2222

## References
- https://github.com/woodpecker-ci/woodpecker/security/advisories/GHSA-4gcf-5m39-98mc
- https://nvd.nist.gov/vuln/detail/CVE-2023-40034
- https://github.com/woodpecker-ci/woodpecker/pull/2221
- https://github.com/woodpecker-ci/woodpecker/pull/2222
- https://github.com/woodpecker-ci/woodpecker/commit/6e4c2f84cc84661d58cf1c0e5c421a46070bb105
- https://github.com/woodpecker-ci/woodpecker
- https://github.com/woodpecker-ci/woodpecker/releases/tag/v1.0.2
