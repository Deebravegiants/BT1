# [C] Deep Java Library path traversal issue

## Summary
Severity: Critical
Advisory: GHSA-jcrp-x7w3-ffmg
CVE: CVE-2025-0851
CWE: CWE-22, CWE-36
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-29
Source: https://github.com/advisories/GHSA-jcrp-x7w3-ffmg
Type: github-advisory

## Affected
- Maven: `ai.djl:api` — affected >=0 <0.31.1

## Details
## Summary

[Deep Java Library (DJL)](https://docs.djl.ai/master/index.html) is an open-source, high-level, engine-agnostic Java framework for deep learning. DJL is designed to be easy to get started with and simple to use for Java developers. DJL provides a native Java development experience and functions like any other regular Java library.

DJL provides utilities for extracting tar and zip model archives that are used when loading models for use with DJL. These utilities were found to contain issues that do not protect against absolute path traversal during the extraction process.

## Impact

An issue exists with DJL's untar and unzip functionalities. Specifically, it is possible to create an archive on a Windows system, and when extracted on a MacOS or Linux system, write artifacts outside the intended destination during the extraction process. The reverse is also true for archives created on MacOS/Linux systems and extracted on Windows systems.

Impacted versions: 0.1.0 - 0.31.0

## Patches

This issue has been patched in DJL 0.31.1 [1]

## Workarounds

Do not use model archive files from sources you do not trust. You should only use model archives from official sources like the DJL Model Zoo, or models that you have created and packaged yourself.

## References

If you have any questions or comments about this advisory, we ask that you contact AWS/Amazon Security via our vulnerability reporting page [2] or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

[1] https://github.com/deepjavalibrary/djl/tree/v0.31.1
[2] https://aws.amazon.com/security/vulnerability-reporting

## References
- https://github.com/deepjavalibrary/djl/security/advisories/GHSA-jcrp-x7w3-ffmg
- https://nvd.nist.gov/vuln/detail/CVE-2025-0851
- https://github.com/deepjavalibrary/djl/commit/7415cc5f72aae69ea9716a5e4f709af03a77a619
- https://aws.amazon.com/security/security-bulletins/AWS-2025-003
- https://github.com/deepjavalibrary/djl
- https://github.com/deepjavalibrary/djl/releases/tag/v0.31.1
