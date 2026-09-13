# [H] Woodpecker's custom workspace allow to overwrite plugin entrypoint executable

## Summary
Severity: High
Advisory: GHSA-xw35-rrcp-g7xm
CVE: CVE-2024-41121
CWE: CWE-22, CWE-74
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-19
Source: https://github.com/advisories/GHSA-xw35-rrcp-g7xm
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
https://github.com/woodpecker-ci/woodpecker/pull/3933

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
**Enable the "gated" repo feature and review each change upfront**

### References
- https://github.com/woodpecker-ci/woodpecker/pull/3933
- https://github.com/woodpecker-ci/woodpecker-security/pull/11
- https://github.com/woodpecker-ci/woodpecker-security/issues/8 (info will be published later at https://github.com/woodpecker-ci/woodpecker/issues/3924)
- https://github.com/woodpecker-ci/woodpecker-security/issues/9 (info will be published later at https://github.com/woodpecker-ci/woodpecker/issues/3924)
- https://github.com/woodpecker-ci/woodpecker/issues/3924 (info will be published later once we got adoption of the update)

### Credits

- Daniel Kilimnik [@D_K_Dev](https://x.com/D_K_Dev) (Neodyme AG)
- Felipe Custodio Romero [@_localo_](https://x.com/_localo_) (Neodyme AG)

## References
- https://github.com/woodpecker-ci/woodpecker/security/advisories/GHSA-xw35-rrcp-g7xm
- https://nvd.nist.gov/vuln/detail/CVE-2024-41121
- https://github.com/woodpecker-ci/woodpecker-security/issues/8
- https://github.com/woodpecker-ci/woodpecker-security/issues/9
- https://github.com/woodpecker-ci/woodpecker/issues/3924
- https://github.com/woodpecker-ci/woodpecker-security/pull/11
- https://github.com/woodpecker-ci/woodpecker/pull/3933
- https://github.com/woodpecker-ci/woodpecker/commit/764329ed1dbc47c4a517ccc749e3feb34059fac8
- https://github.com/woodpecker-ci/woodpecker
- https://pkg.go.dev/vuln/GO-2024-2999
