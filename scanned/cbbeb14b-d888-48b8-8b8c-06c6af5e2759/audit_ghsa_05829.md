# [M] AWS CLI: Disabled SSH host key verification in Amazon AWS CLI EMR helper commands

## Summary
Severity: Medium
Advisory: GHSA-hqvf-45jj-mccq
CVE: CVE-2026-18654
CWE: CWE-322
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-hqvf-45jj-mccq
Type: github-advisory

## Affected
- PyPI: `awscli` — affected >=0 <1.45.28

## Details
### Summary
The AWS Command Line Interface (AWS CLI) is a unified tool to manage AWS services from the command line. An issue exists where the EMR SSH helper commands (`aws emr ssh`, `aws emr socks`, `aws emr put`, `aws emr get`) passed `StrictHostKeyChecking=no` to the underlying SSH client, disabling host key verification.

### Impact
A network-positioned actor could perform a man-in-the-middle action to intercept SSH sessions and file transfers between the client and EMR cluster instances. Successful exploitation requires the actor to have network access on the path between the client machine and the EMR cluster endpoint. This could result in full visibility of commands executed, files transferred, and credentials passed over the SSH session.

Impacted versions: AWS CLI v1 <= 1.45.27, AWS CLI v2 <= 2.35.2

### Patches
This issue has been addressed in AWS CLI v1 version 1.45.28 and AWS CLI v2 version 2.35.3. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

### Workarounds
There is no workaround. The insecure SSH option was hardcoded and could not be overridden by the user.

### References
If you have any questions or comments about this advisory, we ask that you contact AWS Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

### Acknowledgement
We would like to thank Ali Sunbul for collaborating on this issue through the coordinated vulnerability disclosure process.

## References
- https://github.com/aws/aws-cli/security/advisories/GHSA-hqvf-45jj-mccq
- https://nvd.nist.gov/vuln/detail/CVE-2026-18654
- https://aws.amazon.com/security/security-bulletins/2026-071-aws
- https://github.com/aws/aws-cli
- https://github.com/aws/aws-cli/blob/develop/CHANGELOG.rst
- https://github.com/aws/aws-cli/blob/v2/CHANGELOG.rst
