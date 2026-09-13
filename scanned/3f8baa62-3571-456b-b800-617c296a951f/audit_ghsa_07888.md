# [M]  Gogs user can update repository content with read-only permission

## Summary
Severity: Medium
Advisory: GHSA-5qhx-gwfj-6jqr
CVE: CVE-2026-23632
CWE: CWE-862, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-5qhx-gwfj-6jqr
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.13.4

## Details
## Vulnerability Description

The endpoint
`PUT /repos/:owner/:repo/contents/*`
does not require write permissions and allows access with **read permission only** via `repoAssignment()`.

After passing the permission check, `PutContents()` invokes `UpdateRepoFile()`, which results in:

* Commit creation
* Execution of `git push`

As a result, a token with **read-only permission** can be used to modify repository contents.

---

## Attack Prerequisites

* Possession of a valid access token
* Read permission on the target repository
  (public repository or collaborator with read access)

---

## Attack Scenario

1. The attacker accesses the target repository with a read-only token
2. The attacker sends a `PUT /contents` request to update an arbitrary file
3. The server creates a commit and performs a git push on behalf of the attacker

---

## Potential Impact

* Source code tampering
* Injection of backdoors
* Compromise of release artifacts and distributed packages

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-5qhx-gwfj-6jqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-23632
- https://github.com/gogs/gogs/pull/8102/commits/b6afcdb2e8d291e2adaaf6a8b7f88d240606515d
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.13.4
