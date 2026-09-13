# [H] GitHub PAT written to debug artifacts

## Summary
Severity: High
Advisory: GHSA-vqf5-2xx6-9wfm
CVE: CVE-2025-24362
CWE: CWE-215, CWE-532
Ecosystem: GitHub Actions
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-01-24
Source: https://github.com/advisories/GHSA-vqf5-2xx6-9wfm
Type: github-advisory

## Affected
- GitHub Actions: `github/codeql-action` — affected >=3.26.11 <3.28.3
- GitHub Actions: `github/codeql-action` — affected >=2.26.11

## Details
### Impact summary

In some circumstances, debug artifacts uploaded by the CodeQL Action after a failed code scanning workflow run may contain the environment variables from the workflow run, including any secrets that were exposed as environment variables to the workflow. Users with read access to the repository would be able to access this artifact, containing any secrets from the environment.

For some affected workflow runs, the exposed environment variables in the debug artifacts included a valid `GITHUB_TOKEN` for the workflow run, which has access to the repository in which the workflow ran, and all the permissions specified in the workflow or job. The `GITHUB_TOKEN` is valid until the job completes or 24 hours has elapsed, whichever comes first.

Environment variables are exposed only from workflow runs that satisfy all of the following conditions:
- Code scanning workflow configured to scan the Java/Kotlin languages.
- Running in a repository containing Kotlin source code.
- Running with [debug artifacts enabled](https://docs.github.com/en/code-security/code-scanning/troubleshooting-code-scanning/logs-not-detailed-enough).
- Using CodeQL Action versions <= 3.28.2, and CodeQL CLI versions >= 2.9.2 (May 2022) and <= 2.20.2.
- The workflow run fails before the CodeQL database is finalized within the `github/codeql-action/analyze` step.
- Running in any GitHub environment: GitHub.com, GitHub Enterprise Cloud, and GitHub Enterprise Server. (Note: artifacts are only accessible to users within the same GitHub environment with access to the scanned repo.)

The `GITHUB_TOKEN` exposed in this way would only have been valid for workflow runs that satisfy all of the following conditions, in addition to the conditions above:
- Using CodeQL Action versions >= 3.26.11 (October 2024) and <= 3.28.2, or >= 2.26.11 and < 3.
- Running in GitHub.com or GitHub Enterprise Cloud only (not valid on GitHub Enterprise Server).

In rare cases during advanced setup, logging of environment variables may also occur during database creation of Java, Swift, and C/C++. Please read the corresponding CodeQL CLI advisory [GHSA-gqh3-9prg-j95m](https://github.com/github/codeql-cli-binaries/security/advisories/GHSA-gqh3-9prg-j95m) for more details.


### Impact details

In CodeQL CLI versions >= 2.9.2 and <= 2.20.2, the CodeQL Kotlin extractor logs all environment variables by default into an intermediate file during the process of creating a CodeQL database for Kotlin code. 
This is a part of the CodeQL CLI and is invoked by the CodeQL Action for analyzing Kotlin repositories. 
On Actions, the environment variables logged include GITHUB_TOKEN, which grants permissions to the repository being scanned.

The intermediate file containing environment variables is deleted when finalizing the database, so it is not included in a successfully created database. It is, however, included in the debug artifact that is uploaded on a failed analysis run if the CodeQL Action was invoked in debug mode.

Therefore, under these specific circumstances (incomplete database creation using the CodeQL Action in debug mode) an attacker with access to the debug artifact would gain unauthorized access to repository secrets from the environment, including both the `GITHUB_TOKEN` and any user-configured secrets made available via environment variables.

The impact of the `GITHUB_TOKEN` leaked in this environment is limited:
- For workflows on GitHub.com and GitHub Enterprise Cloud using CodeQL Action versions >= 3.26.11 and <= 3.28.2, or >= 2.26.11 and < 3, which in turn use the `actions/artifacts v4` library, the debug artifact is uploaded before the workflow job completes. During this time the `GITHUB_TOKEN` is still valid, providing an opportunity for attackers to gain access to the repository.
- For all other workflows, the debug artifact is uploaded after the workflow job completes, at which point the leaked `GITHUB_TOKEN` has been revoked and cannot be used to access the repository.

### Mitigations

Update to CodeQL Action version 3.28.3 or later, or CodeQL CLI version 2.20.3 or later.

### Patches

This vulnerability has been fixed in CodeQL Action version 3.28.3, which no longer uploads database artifacts in debug mode.
This vulnerability will be fixed in CodeQL CLI version 2.20.3, in which database creation for all languages no longer logs the complete environment by default.

### References

- [Pull request that bundled CodeQL CLI 2.9.2 with Kotlin extractor environment variable logging ](https://github.com/github/codeql-action/pull/1074)
- [Pull request that introduced the `actions/artifacts v4` library, allowing for `GITHUB_TOKEN` exposure in the CodeQL Action debug artifacts before the token was revoked](https://github.com/github/codeql-action/pull/2482)
- [Related security advisory for the CodeQL CLI](https://github.com/github/codeql-cli-binaries/security/advisories/GHSA-gqh3-9prg-j95m)

## References
- https://github.com/github/codeql-action/security/advisories/GHSA-vqf5-2xx6-9wfm
- https://github.com/github/codeql-cli-binaries/security/advisories/GHSA-gqh3-9prg-j95m
- https://nvd.nist.gov/vuln/detail/CVE-2025-24362
- https://github.com/github/codeql-action/pull/1074
- https://github.com/github/codeql-action/pull/2482
- https://github.com/github/codeql-action/commit/519de26711ecad48bde264c51e414658a82ef3fa
- https://docs.github.com/en/code-security/code-scanning/troubleshooting-code-scanning/logs-not-detailed-enough
- https://github.com/github/codeql-action
- https://news.ycombinator.com/item?id=43527044
- https://www.praetorian.com/blog/codeqleaked-public-secrets-exposure-leads-to-supply-chain-attack-on-github-codeql
