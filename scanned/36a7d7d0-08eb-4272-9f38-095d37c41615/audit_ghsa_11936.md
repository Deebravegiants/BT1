# [C] wenxian: Command Injection in GitHub Actions Workflow via `issue_comment.body` 

## Summary
Severity: Critical
Advisory: GHSA-r4fj-r33x-8v88
CVE: CVE-2026-34243
CWE: CWE-20, CWE-77, CWE-78
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-r4fj-r33x-8v88
Type: github-advisory

## Affected
- GitHub Actions: `njzjz/wenxian` — affected >=0

## Details
#### Summary

A GitHub Actions workflow uses untrusted user input from `issue_comment.body` directly inside a shell command, allowing potential command injection and arbitrary code execution on the runner.

#### Details

The workflow is triggered by `issue_comment`, which can be controlled by external users.
In the following step:

```bash
echo identifiers=$(echo "${{ github.event.comment.body }}" | grep -oE '@njzjz-bot .*' | head -n1 | cut -c12- | xargs) >> $GITHUB_OUTPUT
```

the value of `github.event.comment.body` is directly interpolated into a shell command inside `run:`.

Since GitHub Actions evaluates `${{ }}` before execution, attacker-controlled input is injected into the shell context without sanitization. This creates a command injection risk.

Additionally, the extracted value is later reused in another step that constructs output using backticks:

```bash
echo '@${{ github.event.comment.user.login }} Here is the BibTeX entry for `${{ steps.extract-identifiers.outputs.identifiers }}`:'
```

which may further propagate unsafe content.

#### PoC

1. Go to an issue in the repository
2. Post a comment such as:

`@njzjz-bot paper123" ) ; whoami ; #
`

3. Observe whether the command is executed or reflected in logs/output
<img width="658" height="203" alt="poc" src="https://github.com/user-attachments/assets/084ac264-8cb9-4721-8279-26a1da9b891f" />

The injected payload successfully breaks out of the quoted context and executes arbitrary shell commands.

As shown in the workflow logs, the injected `whoami` command is executed, and the output (`runner`) is printed. This confirms that attacker-controlled input from `github.event.comment.body` is interpreted as shell commands.

This demonstrates a clear command injection vulnerability in the workflow.

#### Impact

* Remote attackers can inject arbitrary shell commands via issue comments
* Potential impacts:

  * Execution of arbitrary commands in GitHub Actions runner
  * Access to `GITHUB_TOKEN`
  * Exfiltration of repository data
  * CI/CD pipeline compromise


This issue affects all current versions of the repository as the vulnerable workflow is present in the main branch.

### Suggested Fix

Avoid directly interpolating untrusted user input into shell commands.

Instead, pass `github.event.comment.body` through an environment variable and reference it safely within the script:

```yaml
- name: Extract identifiers
  id: extract-identifiers
  env:
    COMMENT_BODY: ${{ github.event.comment.body }}
  run: |
    identifiers=$(echo "$COMMENT_BODY" | grep -oE '@njzjz-bot .*' | head -n1 | cut -c12- | xargs)
    echo "identifiers=$identifiers" >> $GITHUB_OUTPUT

## References
- https://github.com/njzjz/wenxian/security/advisories/GHSA-r4fj-r33x-8v88
- https://nvd.nist.gov/vuln/detail/CVE-2026-34243
- https://github.com/njzjz/wenxian
