# [M] Woodpecker's custom environment variables allow to alter execution flow of plugins

## Summary
Severity: Medium
Advisory: GHSA-3wf2-2pq4-4rvc
CVE: CVE-2024-41122
CWE: CWE-74
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-19
Source: https://github.com/advisories/GHSA-3wf2-2pq4-4rvc
Type: github-advisory

## Affected
- Go: `go.woodpecker-ci.org/woodpecker/v2` — affected >=0 <2.7.0
- Go: `go.woodpecker-ci.org/woodpecker` — affected >=0 <2.7.0

## Details
### Impact
The server allow to create any user who can trigger a pipeline run malicious workflows:
- Those workflows can either lead to a host takeover that runs the agent executing the workflow.
- Or allow to extract the secrets who would be normally provided to the plugins who's entrypoint are overwritten.

### Patches
https://github.com/woodpecker-ci/woodpecker/pull/3909
https://github.com/woodpecker-ci/woodpecker/pull/3934

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
**Enable the "gated" repo feature and review each change upfront of running**

### References
- https://github.com/woodpecker-ci/woodpecker/pull/3909
- https://github.com/woodpecker-ci/woodpecker/pull/3934
- https://github.com/woodpecker-ci/woodpecker-security/issues/10 (info will be published later at https://github.com/woodpecker-ci/woodpecker/issues/3929)
- https://github.com/woodpecker-ci/woodpecker/issues/3929 (info will be published later once we got adoption of the update)

### Credits

- Daniel Kilimnik [@D_K_Dev](https://x.com/D_K_Dev) (Neodyme AG)
- Felipe Custodio Romero [@_localo_](https://x.com/_localo_) (Neodyme AG)

## References
- https://github.com/woodpecker-ci/woodpecker/security/advisories/GHSA-3wf2-2pq4-4rvc
- https://nvd.nist.gov/vuln/detail/CVE-2024-41122
- https://github.com/woodpecker-ci/woodpecker-security/issues/10
- https://github.com/woodpecker-ci/woodpecker/issues/3929
- https://github.com/woodpecker-ci/woodpecker/pull/3909
- https://github.com/woodpecker-ci/woodpecker/pull/3934
- https://github.com/woodpecker-ci/woodpecker/commit/8aa3e5ec82c92eca3279e4be68625111eeedf1c4
- https://github.com/woodpecker-ci/woodpecker
- https://pkg.go.dev/vuln/GO-2024-2998
