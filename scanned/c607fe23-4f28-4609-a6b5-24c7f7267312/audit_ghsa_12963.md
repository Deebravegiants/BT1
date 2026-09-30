# [M] Improper log output when using GitHub Status Notifications in spinnaker

## Summary
Severity: Medium
Advisory: GHSA-rq5c-hvw6-8pr7
CVE: CVE-2023-39348
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-29
Source: https://github.com/advisories/GHSA-rq5c-hvw6-8pr7
Type: github-advisory

## Affected
- Go: `github.com/spinnaker/spinnaker` — affected >=0
- Go: `github.com/spinnaker/spinnaker` — affected >=1.29.0
- Go: `github.com/spinnaker/spinnaker` — affected >=1.30.0
- Go: `github.com/spinnaker/spinnaker` — affected >=1.31.0

## Details
### Impact
ONLY IMPACTS those use GitHub Status Notifications

Log output when updating GitHub status is improperly set to FULL always.  It's recommended to apply the patch and rotate the GitHub token used for github status notifications.  Given that this would output github tokens to a log system, the risk is slightly higher than a "low" since token exposure could grant elevated access to repositories outside of control.  If using READ restricted tokens, the exposure is such that the token itself could be used to access resources otherwise restricted from reads.

### Patches
Patch is in progress.  https://github.com/spinnaker/echo/pull/1316

### Workarounds
Disable GH Status Notifications.  Filter your logs for Echo log data.  Use read-only tokens that are limited in scope.

### References
sig-security in slack: https://spinnakerteam.slack.com/archives/CFN8F5UR2

## References
- https://github.com/spinnaker/spinnaker/security/advisories/GHSA-rq5c-hvw6-8pr7
- https://nvd.nist.gov/vuln/detail/CVE-2023-39348
- https://github.com/spinnaker/echo/pull/1316
- https://github.com/spinnaker/spinnaker
