# [H] Rebuild-bot workflow may allow unauthorised repository modifications

## Summary
Severity: High
Advisory: GHSA-gg2g-m5wc-vccq
CVE: CVE-2021-21423
CWE: CWE-527
Ecosystem: PyPI, npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-04-06
Source: https://github.com/advisories/GHSA-gg2g-m5wc-vccq
Type: github-advisory

## Affected
- npm: `projen` — affected >=0.6.0 <0.16.41
- PyPI: `projen` — affected >=0 <0.16.41

## Details
### Impact

`projen` is a project generation tool that synthesizes project configuration files such as `package.json`, `tsconfig.json`, `.gitignore`, GitHub Workflows, `eslint`, `jest`, and more, from a well-typed definition written in JavaScript. Users of projen's `NodeProject` project type (including any project type derived from it) include a `.github/workflows/rebuild-bot.yml` workflow that may allow any GitHub user to trigger execution of un-trusted code in the context of the "main" repository (as opposed to that of a fork). In some situations, such untrusted code may potentially be able to commit to the "main" repository.

The rebuild-bot workflow is triggered by comments including `@projen rebuild` on pull-request to trigger a re-build of the projen project, and updating the pull request with the updated files. This workflow is triggered by an `issue_comment` event, and thus always executes with a `GITHUB_TOKEN` belonging to the repository into which the pull-request is made (this is in contrast with workflows triggered by `pull_request` events, which always execute with a `GITHUB_TOKEN` belonging to the repository from which the pull-request is made).

Repositories that do not have branch protection configured on their default branch (typically `main` or `master`) could possibly allow an untrusted user to gain access to secrets configured on the repository (such as NPM tokens, etc). Branch protection prohibits this escalation, as the managed `GITHUB_TOKEN` would not be able to modify the contents of a protected branch and affected workflows must be defined on the default branch. 

### Patches

The issue was mitigated in version `0.16.41` of the `projen` tool, which removes the `issue_comment` trigger from this workflow. Version `0.17.0` of projen completely removes the `rebuild-bot.yml` workflow.

### Workarounds

The recommended way to address the vulnerability is to upgrade `projen`. Users who cannot upgrade `projen` may also remove the `.github/workflows/rebuild-bot.yml` file and add it to their `.gitignore` file (via `projenrc.js`) to mitigate the issue.

### References

The `rebuild-bot.yml` workflow managed by `projen` is only one occurrence of a GitHub Workflows mis-configuration, but it may also be present in other workflows not managed by `projen` (either hand-written, or managed by other tools). For more information on this class of issues, the [Keeping your GitHub Actions and workflows secure: Preventing pwn requests][1] article provides a great overview of the problem.
 

[1]: https://securitylab.github.com/research/github-actions-preventing-pwn-requests

## References
- https://github.com/projen/projen/security/advisories/GHSA-gg2g-m5wc-vccq
- https://nvd.nist.gov/vuln/detail/CVE-2021-21423
- https://github.com/projen/projen/commit/36030c6a4b1acd0054673322612e7c70e9446643
- https://github.com/projen/projen
- https://github.com/pypa/advisory-database/tree/main/vulns/projen/PYSEC-2021-111.yaml
- https://www.npmjs.com/package/projen
