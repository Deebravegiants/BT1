# [H] Coder logs sensitive objects unsanitized

## Summary
Severity: High
Advisory: GHSA-jf75-p25m-pw74
CVE: CVE-2025-66411
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-03
Source: https://github.com/advisories/GHSA-jf75-p25m-pw74
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=0 <2.26.5
- Go: `github.com/coder/coder/v2` — affected >=2.27.0 <2.27.7
- Go: `github.com/coder/coder/v2` — affected >=2.28.0 <2.28.4

## Details
## Summary
Workspace Agent manifests containing sensitive values were logged in plaintext unsanitized

## Details
By default Workspace Agent logs are redirected to [stderr](https://linux.die.net/man/3/stderr)
https://github.com/coder/coder/blob/a8862be546f347c59201e2219d917e28121c0edb/cli/agent.go#L432-L439

[Workspace Agent Manifests](https://coder.com/docs/reference/agent-api/schemas#agentsdkmanifest) containing sensitive environment variables were logged insecurely
https://github.com/coder/coder/blob/7beb95fd56d2f790502e236b64906f8eefb969bd/agent/agent.go#L1090

An attacker with limited local access to the Coder Workspace (VM, K8s Pod etc.) or a third-party system ([SIEM](https://csrc.nist.gov/glossary/term/security_information_and_event_management_tool), logging stack) could access those logs

This behavior opened room for unauthorized access and privilege escalation

## Impact
Impact varies depending on the environment variables set in a given workspace

## Patches
[Fix](https://github.com/coder/coder/commit/e2a46393fce40bc630df3293c1ee66a596277289) was released & backported:
- https://github.com/coder/coder/releases/tag/v2.28.4
- https://github.com/coder/coder/releases/tag/v2.27.7
- https://github.com/coder/coder/releases/tag/v2.26.5

## Workarounds
One potential workaround is to disable Workspace Agent Logs by setting following configuration option
`CODER_AGENT_LOGGING_HUMAN=/dev/null` 
> platform operators are advised to upgrade their deployments

## References
- https://github.com/coder/coder/security/advisories/GHSA-jf75-p25m-pw74
- https://nvd.nist.gov/vuln/detail/CVE-2025-66411
- https://github.com/coder/coder/pull/20968
- https://github.com/coder/coder/commit/06c6abbe0935f9213c1588add60a396da5762e1c
- https://github.com/coder/coder/commit/a75205a559211c8aa494b1a16750d114b263f24a
- https://github.com/coder/coder/commit/e2a46393fce40bc630df3293c1ee66a596277289
- https://github.com/coder/coder
- https://github.com/coder/coder/releases/tag/v2.26.5
- https://github.com/coder/coder/releases/tag/v2.27.7
- https://github.com/coder/coder/releases/tag/v2.28.4
