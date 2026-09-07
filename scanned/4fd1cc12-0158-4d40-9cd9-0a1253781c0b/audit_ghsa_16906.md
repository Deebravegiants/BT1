# [M] Temporal UI Server cross-site scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8f25-w7qj-r7hc
CVE: CVE-2024-2435
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-04-02
Source: https://github.com/advisories/GHSA-8f25-w7qj-r7hc
Type: github-advisory

## Affected
- Go: `github.com/temporalio/ui-server/v2` — affected >=0 <2.25.0

## Details
For an attacker with pre-existing access to send a signal to a workflow, the attacker can make the signal name a script that executes when a victim views that signal. The XSS is in the timeline page displaying the workflow execution details of the workflow that was sent the crafted signal.
Access to send a signal to a workflow is determined by how you configured the authorizer on your server. This includes any entity with permission to directly call SignalWorkflowExecution or SignalWithStartWorkflowExecution, or any entity can deploy a worker that has access to call workflow progress APIs (specifically RespondWorkflowTaskCompleted).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2435
- https://github.com/temporalio/ui-server
- https://github.com/temporalio/ui-server/releases/tag/v2.25.0
