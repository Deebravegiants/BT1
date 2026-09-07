# [H] Gogs: Release tag option injection in release deletion

## Summary
Severity: High
Advisory: GHSA-v9vm-r24h-6rqm
CVE: CVE-2026-26194
CWE: CWE-88
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-v9vm-r24h-6rqm
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.2

## Details
### Summary

There is a security issue in Gogs where deleting a release can fail if a user-controlled tag name is passed to Git without the right separator, allowing Git option injection and therefore interfering with the process.

### Affected Component

  - internal/database/release.go
    `process.ExecDir(..., "git", "tag", "-d", rel.TagName)`

### Details

  `rel.TagName` is used as a CLI argument to `git tag -d` without `--` or `--end-of-options`.
  If the tag name begins with `-`, Git parses it as a flag.

  The prior mitigation is incomplete. There is path sanitization in place during creation:

  - internal/database/release.go
    `r.TagName = strings.TrimLeft(r.TagName, "-")`

  But it only covers one creation path and does not reliably protect tag deletions, such as tags added through `git push` or ref updates.

**Exploit Conditions**
1. An attacker can add a tag name that starts with a dash into the repository.
2. A user with permission to delete releases triggers it through the web UI or API.

### Recommended Fix

1. Add end-of-options in release deletion:
      - `git tag -d -- <tagName>`
2. It is better to use the safe git-module deletion helper since it handles options properly.
3. All Git commands should be audited for user input, ensuring that the end-of-options separator is always used.

### Impact
  - Option injection into `git tag -d`
  - Tag/release deletion can fail or behave unexpectedly
  - Operational denial of service in release cleanup workflows
  - Potential release metadata inconsistency

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-v9vm-r24h-6rqm
- https://nvd.nist.gov/vuln/detail/CVE-2026-26194
- https://github.com/gogs/gogs/pull/8175
- https://github.com/gogs/gogs/commit/a000f0c7a632ada40e6829abdeea525db4c0fc2d
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.2
