# [H] Insecure path traversal in Git Trigger Source can lead to arbitrary file read

## Summary
Severity: High
Advisory: GHSA-qpgx-64h2-gc3c
CVE: CVE-2022-25856
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-qpgx-64h2-gc3c
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-events` — affected >=0 <1.7.1

## Details
### Impact
A path traversal issue was found in the `(g *GitArtifactReader).Read() API. Read()` calls into `(g *GitArtifactReader).readFromRepository()` that opens and reads the file that contains the trigger resource definition:

```go
func (g *GitArtifactReader) readFromRepository(r *git.Repository, dir string)
```

No checks are made on this file at read time, which could lead an attacker to read files anywhere on the system. This could be achieved by either using symbolic links, or putting `../` in the path.

### Patches
A patch for this vulnerability has been released in the following Argo Events version:

v1.7.1

### Credits
Disclosed by [Ada Logics](https://adalogics.com/) in a security audit sponsored by CNCF and facilitated by OSTIF.

### For more information
Open an issue in the [Argo Events issue tracker](https://github.com/argoproj/argo-events/issues) or [discussions](https://github.com/argoproj/argo-events/discussions)
Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-events

## References
- https://github.com/argoproj/argo-events/security/advisories/GHSA-qpgx-64h2-gc3c
- https://nvd.nist.gov/vuln/detail/CVE-2022-25856
- https://github.com/argoproj/argo-events/issues/1947
- https://github.com/argoproj/argo-events/pull/1965
- https://github.com/argoproj/argo-events/commit/d0f66dbce78bc31923ca057b20fc722aa24ca961
- https://github.com/argoproj/argo-events
- https://pkg.go.dev/vuln/GO-2022-0492
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMARGOPROJARGOEVENTSSENSORSARTIFACTS-2864522
