# [H] Potential Actions command injection in output filenames (GHSL-2023-275)

## Summary
Severity: High
Advisory: GHSA-ghm2-rq8q-wrhc
CVE: CVE-2023-52137
CWE: CWE-20, CWE-77
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2024-01-02
Source: https://github.com/advisories/GHSA-ghm2-rq8q-wrhc
Type: github-advisory

## Affected
- GitHub Actions: `tj-actions/verify-changed-files` — affected >=0 <17

## Details
### Summary
The [`tj-actions/verify-changed-files`](https://github.com/tj-actions/verify-changed-files) action allows for command injection in changed filenames, allowing an attacker to execute arbitrary code and potentially leak secrets.

### Details
The [`verify-changed-files`](https://github.com/tj-actions/verify-changed-files) workflow returns the list of files changed within a workflow execution.

This could potentially allow filenames that contain special characters such as `;` and \` (backtick) which can be used by an attacker to take over the [GitHub Runner](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners) if the output value is used in a raw fashion (thus being directly replaced before execution) inside a `run` block. By running custom commands an attacker may be able to steal **secrets** such as `GITHUB_TOKEN` if triggered on other events than `pull_request`. For example on `push`.

#### Proof of Concept

1. Submit a pull request to the repository with a new file injecting a command. For example `$(whoami).txt` would be a valid filename.
2. Upon approval of the workflow (triggered by the pull request), the action will get executed and the malicious pull request filename will flow into the `List all changed files tracked and untracked files` step.

```yaml
- name: List all changed files tracked and untracked files
  run: |
    echo "Changed files: ${{ steps.verify-changed-files.outputs.changed_files }}"
```

Example output:

```yaml
##[group]Run echo "Changed files: $(whoami).txt"
  echo "Changed files: $(whoami).txt"[0m
shell: /usr/bin/bash -e {0}
##[endgroup]
Changed files: runner.txt
```

### Impact
This issue may lead to arbitrary command execution in the GitHub Runner.

### Resolution
- A new `safe_output` input would be enabled by default and return filename paths escaping special characters like ;, ` (backtick), $, (), etc for bash environments.

- A safe recommendation of using environment variables to store unsafe outputs.

```yaml
- name: List all changed files tracked and untracked files
  env:
     CHANGED_FILES: ${{ steps.verify-changed-files.outputs.changed_files }}
  run: |
    echo "Changed files: $CHANGED_FILES"
```


### Resources

* [Keeping your GitHub Actions and workflows secure Part 2: Untrusted input](https://securitylab.github.com/research/github-actions-untrusted-input/)
* [Keeping your GitHub Actions and workflows secure Part 1: Preventing pwn requests](https://securitylab.github.com/research/github-actions-preventing-pwn-requests/)

## References
- https://github.com/tj-actions/verify-changed-files/security/advisories/GHSA-ghm2-rq8q-wrhc
- https://nvd.nist.gov/vuln/detail/CVE-2023-52137
- https://github.com/tj-actions/verify-changed-files/commit/498d3f316f501aa72485060e8c96fde7b2014f12
- https://github.com/tj-actions/verify-changed-files/commit/592e305da041c09a009afa4a43c97d889bed65c3
- https://github.com/tj-actions/verify-changed-files
