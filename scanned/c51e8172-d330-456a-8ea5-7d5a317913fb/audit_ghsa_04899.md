# [H] aws-cdk-lib: OS Command Injection in NodejsFunction Bundling

## Summary
Severity: High
Advisory: GHSA-999r-qq7v-r334
CVE: CVE-2026-11417
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-999r-qq7v-r334
Type: github-advisory

## Affected
- npm: `aws-cdk-lib` — affected >=0 <2.246.0

## Details
### Summary
AWS CDK (`aws-cdk-lib`) is an open-source framework for defining cloud infrastructure in code and provisioning it through AWS CloudFormation. OS command injection in the `NodejsFunction` local bundling pipeline in `aws-cdk-lib` before 2.245.0 (2.246.0 on Windows) might allow a threat actor who controls the value of one or more bundling properties (`externalModules`, `define`, `loader`, `inject`, or `esbuildArgs`) to execute arbitrary commands on the host running the CDK toolchain via injected shell metacharacters. This issue requires the threat actor to control the value of one or more of the affected bundling properties in the CDK application.

### Impact
During local Lambda bundling, `NodejsFunction` assembled an esbuild command string from the bundling properties `externalModules`, `define`, `loader`, `inject`, and `esbuildArgs` and executed it via a shell (`bash -c` on Linux/macOS, `cmd /c` on Windows) through `spawnSync`. The property values were interpolated without escaping or validation, so values containing shell metacharacters could execute arbitrary commands with the privileges of the user running `cdk synth`, `cdk deploy`, or `cdk diff`. Exploitation requires a threat actor to control one or more of the affected property values in the CDK application — for example via an untrusted npm dependency that vends a wrapper construct, or via a pull request that introduces untrusted values.

### Impacted versions: 
< 2.245.0 (on Windows, < 2.246.0)

### Patches
This issue has been addressed in `aws-cdk-lib` version 2.245.0 (PR #37292), with a Windows-specific regression fix in 2.246.0 (PR #37412). The fix replaces shell-based command execution with array-based `spawnSync` invocation that does not invoke a shell. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

### Workarounds
Ensure the values supplied to `NodejsFunction` bundling properties (`externalModules`, `define`, `loader`, `inject`, `esbuildArgs`) originate only from trusted sources, and audit third-party constructs and pull requests that set them. Upgrading to a fixed version is the recommended remediation.

### References
If you have any questions or comments about this advisory, we ask that you contact AWS Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

### Acknowledgement 
AWS would like to thank the external researcher Hesham Ashraf who reported this issue through the AWS Vulnerability Disclosure Program (HackerOne) for collaborating on it through the coordinated vulnerability disclosure process.

## References
- https://github.com/aws/aws-cdk/security/advisories/GHSA-999r-qq7v-r334
- https://nvd.nist.gov/vuln/detail/CVE-2026-11417
- https://github.com/aws/aws-cdk/pull/37292
- https://github.com/aws/aws-cdk/pull/37412
- https://aws.amazon.com/security/security-bulletins/2026-041-aws
- https://github.com/aws/aws-cdk
- https://github.com/aws/aws-cdk/releases/tag/v2.245.0
