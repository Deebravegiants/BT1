# [H] Super-linter is vulnerable to command injection via crafted filenames in Super-linter Action

## Summary
Severity: High
Advisory: GHSA-r79c-pqj3-577x
CVE: CVE-2026-25761
CWE: CWE-77
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-r79c-pqj3-577x
Type: github-advisory

## Affected
- GitHub Actions: `super-linter/super-linter` — affected >=6.0.0 <8.3.1
- GitHub Actions: `super-linter/super-linter/slim` — affected >=6.0.0 <8.3.1

## Details
### Summary

The Super-linter GitHub Action is vulnerable to **command injection via crafted filenames**. When this action is used in downstream GitHub Actions workflows, an attacker can submit a pull request that introduces a file whose **name** contains shell command substitution syntax, such as `$(...)`. In affected Super-linter versions, runtime scripts may execute the embedded command during file discovery processing, enabling arbitrary command execution in the workflow runner context. This can be used to disclose the job’s `GITHUB_TOKEN` depending on how the workflow configures permissions.

### Details

The issue appears originates in the logic that scans the repository for changed files to check.

1. Use a workflow that runs Super-linter on `pull_request` events.
2. Open a pull request that adds a new file with a crafted filename containing command substitution and an outbound request that includes `$GITHUB_TOKEN`.
3. Run the workflow.  

### Impact

- **Arbitrary command execution** in the context of the workflow run that invokes Super-linter (triggered by attacker-controlled filenames in a PR).
- **Credential exposure / misuse:** the injected command can read environment variables available to the action, including `GITHUB_TOKEN`.

The level of exposure depends on the source of the pull request.

To actively exploit the vulnerability, an attacker needs have the ability to run workflows without any [approval from the repository admin](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/approve-runs-from-forks).

Also, the `GITHUB_TOKEN` needs to have unconstrained access to repository resources. Even in that case, for pull request coming from forked repositories, no secrets are passed to the forked repository when running workflows triggered by `pull_request` events, and the `GITHUB_TOKEN` drops and write permission on the source repository [source](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflows-in-forked-repositories).

Finally, although not specific to this vulnerability, we recommend auditing `workflow_call` and `pull_request_target` workflows because they can lead to compromise, regardless of whether you're using Super-linter, or not, as [explained by this GitHub Enterprise doc](https://docs.github.com/en/enterprise-cloud@latest/actions/reference/security/secure-use#mitigating-the-risks-of-untrusted-code-checkout).

## References
- https://github.com/super-linter/super-linter/security/advisories/GHSA-r79c-pqj3-577x
- https://nvd.nist.gov/vuln/detail/CVE-2026-25761
- https://github.com/super-linter/super-linter
- https://github.com/super-linter/super-linter/releases/tag/v8.3.1
