# [C] AWS Amplify Studio UI Component Properties Has an Input Validation Issue

## Summary
Severity: Critical
Advisory: GHSA-hf3j-86p7-mfw8
CVE: CVE-2025-4318
CWE: CWE-95
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-hf3j-86p7-mfw8
Type: github-advisory

## Affected
- npm: `@aws-amplify/codegen-ui-react` — affected >=0 <2.20.3

## Details
### Summary
The AWS Amplify Studio [amplify-codegen-ui](https://github.com/aws-amplify/amplify-codegen-ui) is a package that generates front-end code from UI Builder entities (components, forms, views, and themes) primarily used in AWS Amplify Studio for component previews and in AWS Command Line Interface (AWS CLI) for generating component files in customers' local applications.

An issue exists in the Amplify Studio property binding process of the `amplify-codegen-ui `package that could potentially allow an authenticated user to run arbitrary JavaScript code during the component rendering and build process.

### Impact
When importing a component schema using the [create-component](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/amplifyuibuilder/create-component.html) command, Amplify Studio will import and generate the component on the users' behalf. The expression-binding function does not validate the component schema properties before converting them to expressions. As a result, an authenticated user who can create or modify components could run arbitrary JavaScript code during the component rendering and build process. 

**Impacted versions: <=2.20.2**

### Patches
This issue has been addressed partially in version [2.20.3](https://github.com/aws-amplify/amplify-codegen-ui/pull/1174) and additional fixes in [2.20.4](https://github.com/aws-amplify/amplify-codegen-ui/pull/1196). We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

### Workarounds
There are no workarounds. Upgrade to version [2.20.4](https://github.com/aws-amplify/amplify-codegen-ui/releases/tag/v2.20.4).

If you have any questions or comments about this advisory, AWS asks that you contact AWS/Amazon Security via the [issue-reporting page](https://aws.amazon.com/security/vulnerability-reporting/) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

### Credit
AWS would like to thank `ray the bounty hunter` for collaborating on this issue through the coordinated issue disclosure process.

## References
- https://github.com/aws-amplify/amplify-codegen-ui/security/advisories/GHSA-hf3j-86p7-mfw8
- https://nvd.nist.gov/vuln/detail/CVE-2025-4318
- https://github.com/aws-amplify/amplify-codegen-ui/commit/ca98c38b7c3d69ae7c94d2f62b51e32e8165dae6
- https://aws.amazon.com/security/security-bulletins/AWS-2025-010
- https://blog.securelayer7.net/cve-2025-4318-aws-amplify-rce
- https://github.com/aws-amplify/amplify-codegen-ui
- https://github.com/aws-amplify/amplify-codegen-ui/releases/tag/v2.20.3
