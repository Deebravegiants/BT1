# [M] @actions/core has Delimiter Injection Vulnerability in exportVariable

## Summary
Severity: Medium
Advisory: GHSA-7r3h-m5j6-3q42
CVE: CVE-2022-35954
CWE: CWE-74, CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-7r3h-m5j6-3q42
Type: github-advisory

## Affected
- npm: `@actions/core` — affected >=0 <1.9.1

## Details
## Impact

The `core.exportVariable` function uses a well known delimiter that attackers can use to break out of that specific variable and assign values to other arbitrary variables. Workflows that write untrusted values to the `GITHUB_ENV` file may cause the path or other environment variables to be modified without the intention of the workflow or action author.

## Patches

Users should upgrade to `@actions/core v1.9.1`.

## Workarounds

If you are unable to upgrade the `@actions/core` package, you can modify your action to ensure that any user input does not contain the delimiter `_GitHubActionsFileCommandDelimeter_` before calling `core.exportVariable`.

## References

[More information about setting-an-environment-variable in workflows](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-environment-variable)

If you have any questions or comments about this advisory:
* Open an issue in [`actions/toolkit`](https://github.com/actions/toolkit/issues)

## References
- https://github.com/actions/toolkit/security/advisories/GHSA-7r3h-m5j6-3q42
- https://nvd.nist.gov/vuln/detail/CVE-2022-35954
- https://github.com/actions/toolkit/commit/4beda9cbc00ba6eefe387a937c21087ccb8ee9df
- https://github.com/actions/toolkit
