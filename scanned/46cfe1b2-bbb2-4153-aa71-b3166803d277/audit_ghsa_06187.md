# [H] jsii-diff: Command Injection via npm: package argument

## Summary
Severity: High
Advisory: GHSA-wcx4-wpfv-mc5c
CVE: CVE-2026-15895
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-wcx4-wpfv-mc5c
Type: github-advisory

## Affected
- npm: `jsii-diff` — affected >=0 <1.131.0

## Details
## Summary

jsii-diff is a command line tool to compare the API differences between two jsii assemblies, and report errors if there are backwards-incompatible changes to the API. An issue exists where specially formatted command line arguments can be used to execute shell commands via this tool.

## Impact
jsii-diff supports downloading packages to compare directly from NPM, so that you can compare a proposed candidate version of your jsii package with an already-published version, by passing an argument that looks like `npm:<package-specifier>`. For example:

```
jsii-diff npm:my-package@latest .
```

By injecting a `;` into the `package-specifier` part of that command, jsii-diff can be tricked into running shell commands. For example:

```
jsii-diff "npm:lodash; touch /tmp/123" .
```

This allows anyone that can control the command-line arguments to jsii-diff to run arbitrary commands with the same permissions as the jsii-diff command itself.

## Patches
This issue has been addressed in jsii-diff version 1.131.0. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

## Workarounds
If you are unable to update, make sure only trusted actors can control the arguments passed to jsii-diff.

## References
If you have any questions or comments about this advisory, AWS asks that you contact AWS Security via the [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/jsii/security/advisories/GHSA-wcx4-wpfv-mc5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-15895
- https://aws.amazon.com/security/security-bulletins/2026-057-aws
- https://github.com/aws/jsii
- https://github.com/aws/jsii/releases/tag/v1.131.0
