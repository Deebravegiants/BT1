# [H] sagemaker-python-sdk Command Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-7pc3-pr3q-58vg
CVE: CVE-2024-34073
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-03
Source: https://github.com/advisories/GHSA-7pc3-pr3q-58vg
Type: github-advisory

## Affected
- PyPI: `sagemaker` — affected >=0 <2.214.3

## Details
### Impact

The capture_dependencies function in `sagemaker.serve.save_retrive.version_1_0_0.save.utils` module before version 2.214.3 allows for potentially unsafe Operating System (OS) Command Injection if inappropriate command is passed as the “requirements_path” parameter. This consequently may allow an unprivileged third party to cause remote code execution, denial of service, affecting both confidentiality and integrity.

Impacted versions: <2.214.3

### Credit

We would like to thank HiddenLayer for collaborating on this issue through the coordinated vulnerability disclosure process.

### Workarounds

Do not override the “requirements_path” parameter of capture_dependencies function in `sagemaker.serve.save_retrive.version_1_0_0.save.utils`, instead use the default value.

### References

If you have any questions or comments about this advisory we ask that you contact AWS/Amazon Security via our vulnerability reporting page [1] or directly via email to aws-security@amazon.com. Please do not create a public GitHub issue.
[1] Vulnerability reporting page: https://aws.amazon.com/security/vulnerability-reporting

Fixed by: https://github.com/aws/sagemaker-python-sdk/pull/4556

## References
- https://github.com/aws/sagemaker-python-sdk/security/advisories/GHSA-7pc3-pr3q-58vg
- https://nvd.nist.gov/vuln/detail/CVE-2024-34073
- https://github.com/aws/sagemaker-python-sdk/pull/4556
- https://github.com/aws/sagemaker-python-sdk/commit/2d873d53f708ea570fc2e2a6974f8c3097fe9df5
- https://github.com/aws/sagemaker-python-sdk
