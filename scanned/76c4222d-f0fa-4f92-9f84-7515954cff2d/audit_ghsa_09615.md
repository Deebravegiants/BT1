# [M] actions-mkdocs: Command Injection via issue title in internal GitHub Actions workflow

## Summary
Severity: Medium
Advisory: GHSA-6p2j-742g-835f
CWE: CWE-77
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-6p2j-742g-835f
Type: github-advisory

## Affected
- GitHub Actions: `Tiryoh/actions-mkdocs` — affected >=0 <0.25.0

## Details
### Summary

External input from `github.event.issue.title` is used unsafely in a shell command in `.github/workflows/release-candidate.yaml`, allowing command injection during workflow execution.

### Details

In `.github/workflows/release-candidate.yaml`, the issue title is interpolated directly into a shell command:

```
export VERSION=$(echo ${{ github.event.issue.title }} | sed -E 's/Release v?([0-9\.]*)/\1/g')
```

Because the issue title is attacker-controlled and is embedded directly into a shell command, shell metacharacters such as command substitution (`$()`) and command separators (`;`) can be interpreted by the shell.

Although the workflow checks that the title starts with `Release `, this condition can still be satisfied by a maliciously crafted input.

### PoC

1. Create or edit an issue with the following title:

   ```
   Release v1.2.3 $(whoami)
   ```

2. Trigger the workflow that processes the issue.

3. Observe that the injected command is executed on the runner.

The workflow logs show that `$(whoami)` is evaluated and its output (`runner`) appears in the command result, confirming that attacker-controlled input is executed within the shell.

<img width="633" height="380" alt="스크린샷 2026-03-27 오후 8 33 43" src="https://github.com/user-attachments/assets/90b38dab-8c53-4a13-8302-158ac5acf051" />


### Impact

This vulnerability allows command injection in the GitHub Actions runner through attacker-controlled issue titles. An attacker may be able to execute arbitrary commands within the context of the affected workflow job.

Depending on the workflow configuration (such as permissions and available secrets), successful exploitation could lead to:

* Unauthorized command execution in the CI environment
* Misuse of the `GITHUB_TOKEN`
* Modification of repository state, release artifacts, or other workflow outputs

If the repository is public and allows untrusted users to create or reopen issues that trigger the workflow, this may be exploitable by external users.

This issue is limited to the repository's internal workflow configuration and does not directly affect downstream users of the published `actions-mkdocs` GitHub Action.

## References
- https://github.com/Tiryoh/actions-mkdocs/security/advisories/GHSA-6p2j-742g-835f
- https://github.com/Tiryoh/actions-mkdocs
