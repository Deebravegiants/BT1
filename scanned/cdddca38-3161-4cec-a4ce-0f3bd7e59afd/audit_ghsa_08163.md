# [M] Trivy Action has a script injection via sourced env file in composite action

## Summary
Severity: Medium
Advisory: GHSA-9p44-j4g5-cfx5
CVE: CVE-2026-26189
CWE: CWE-78
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-9p44-j4g5-cfx5
Type: github-advisory

## Affected
- GitHub Actions: `aquasecurity/trivy-action` — affected >=0.31.0 <0.34.0

## Details
Command Injection in aquasecurity/trivy-action via Unsanitized Environment Variable Export


A command injection vulnerability exists in `aquasecurity/trivy-action` due to improper handling of action inputs when exporting environment variables. The action writes `export VAR=<input>` lines to `trivy_envs.txt` based on user-supplied inputs and subsequently sources this file in `entrypoint.sh`.

Because input values are written without appropriate shell escaping, attacker-controlled input containing shell metacharacters (e.g., `$(...)`, backticks, or other command substitution syntax) may be evaluated during the sourcing process. This can result in arbitrary command execution within the GitHub Actions runner context.

**Severity:**

Moderate

CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N

CWE-78: Improper Neutralization of Special Elements used in an OS Command (‘OS Command Injection’)

**Impact:**

Successful exploitation may lead to arbitrary command execution in the CI runner environment.


**Affected Versions:**

* Versions >= 0.31.0 and <= 0.33.1
* Introduced in commit `7aca5ac`

**Affected Conditions:**

The vulnerability is exploitable when a consuming workflow passes attacker-controlled data into any action input that is written to `trivy_envs.txt`. Access to user input is required by the malicious actor.

A representative exploitation pattern involves incorporating untrusted pull request metadata into an action parameter. For example:

```yaml
- uses: aquasecurity/trivy-action@0.33.1
  with:
    output: "trivy-${{ github.event.pull_request.title }}.sarif"
```

If the pull request title contains shell syntax, it may be executed when the generated environment file is sourced.

**Not Affected:**

* Workflows that do not pass attacker-controlled data into `trivy-action` inputs
* Workflows that upgrade to a patched version that properly escapes shell values or eliminates the `source ./trivy_envs.txt` pattern
* Workflows where user input is not accessible.

**Call Sites:**

* `action.yaml:188` — `set_env_var_if_provided` writes unescaped `export` lines
* `entrypoint.sh:9` — sources `./trivy_envs.txt`

## References
- https://github.com/aquasecurity/trivy-action/security/advisories/GHSA-9p44-j4g5-cfx5
- https://nvd.nist.gov/vuln/detail/CVE-2026-26189
- https://github.com/aquasecurity/trivy-action/commit/7aca5acc9500b463826cc47a47a65ad7d404b045
- https://github.com/aquasecurity/trivy-action/commit/bc61dc55704e2d5704760f3cdab0d09acf16e4ca
- https://github.com/aquasecurity/trivy-action
