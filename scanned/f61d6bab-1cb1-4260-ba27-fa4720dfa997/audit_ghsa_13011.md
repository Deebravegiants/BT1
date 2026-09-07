# [M] Actions expression injection in `filter-test-configs` (`GHSL-2023-181`)

## Summary
Severity: Medium
Advisory: GHSA-hw6r-g8gj-2987
Ecosystem: GitHub Actions
Published: 2023-08-30
Source: https://github.com/advisories/GHSA-hw6r-g8gj-2987
Type: github-advisory

## Affected
- GitHub Actions: `https://github.com/pytorch/pytorch/.github/actions/filter-test-configs` — affected >=0

## Details
The `pytorch/pytorch` `filter-test-configs` workflow is vulnerable to an expression injection in Actions, allowing an attacker to potentially leak secrets and alter the repository using the workflow.

### Details

The [`filter-test-configs`](https://github.com/pytorch/pytorch/blob/ec26947c586dd323d741da80008403664c533f65/.github/actions/filter-test-configs/action.yml) workflow is using the raw `github.event.workflow_run.head_branch` value inside the `filter` step:

```yaml
- name: Select all requested test configurations
  shell: bash
  env:
    GITHUB_TOKEN: ${{ inputs.github-token }}
    JOB_NAME: ${{ steps.get-job-name.outputs.job-name }}
  id: filter
  run: |
    ...
    python3 "${GITHUB_ACTION_PATH}/../../scripts/filter_test_configs.py" \
      ...
      --branch "${{ github.event.workflow_run.head_branch }}"
```

In the event of a repository using `filter-test-configs` in a `pull_request_target`-triggered workflow, an attacker could use a malicious branch name to gain command execution in the step and potentially leak secrets.

```yml
name: Example

on: pull_request_target

jobs:
  example:
    runs-on: ubuntu-latest
    steps:
      - name: Filter
        uses: pytorch/pytorch/.github/actions/filter-test-configs@v2
```

#### Impact

This issue may lead to stealing workflow secrets.

#### Remediation

1. Use an intermediate environment variable for potentially attacker-controlled values such as `github.event.workflow_run.head_branch`:
```yaml
- name: Select all requested test configurations
  shell: bash
  env:
    GITHUB_TOKEN: ${{ inputs.github-token }}
    JOB_NAME: ${{ steps.get-job-name.outputs.job-name }}
    HEAD_BRANCH: ${{ github.event.workflow_run.head_branch }}
  id: filter
  run: |
    ...
    python3 "${GITHUB_ACTION_PATH}/../../scripts/filter_test_configs.py" \
      ...
      --branch "$HEAD_BRANCH"
```

#### Resources

* [CodeQL for JavaScript - Expression injection in Actions](https://codeql.github.com/codeql-query-help/javascript/js-actions-command-injection/)
* [Keeping your GitHub Actions and workflows secure Part 2: Untrusted input](https://securitylab.github.com/research/github-actions-untrusted-input/)
* [Keeping your GitHub Actions and workflows secure Part 1: Preventing pwn requests](https://securitylab.github.com/research/github-actions-preventing-pwn-requests/)

## References
- https://github.com/pytorch/pytorch/security/advisories/GHSA-hw6r-g8gj-2987
- https://github.com/pytorch/pytorch
