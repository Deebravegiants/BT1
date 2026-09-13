# [M] AWS SAM CLI Path Traversal allows file copy to build container

## Summary
Severity: Medium
Advisory: GHSA-px37-jpqx-97q9
CVE: CVE-2025-3047
CWE: CWE-22, CWE-61
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-31
Source: https://github.com/advisories/GHSA-px37-jpqx-97q9
Type: github-advisory

## Affected
- PyPI: `aws-sam-cli` — affected >=0 <1.133.0

## Details
### Summary

The [AWS Serverless Application Model Command Line Interface (AWS SAM CLI)](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/using-sam-cli.html) is an open-source CLI tool that helps Lambda developers to build and develop Lambda applications locally on their computers using Docker.

When running the AWS SAM CLI build process with Docker and symlinks are included in the build files, the container environment allows a user to access privileged files on the host by leveraging the elevated permissions granted to the tool. A user could leverage the elevated permissions to access restricted files via symlinks and copy them to a more permissive location on the container.

Users should [upgrade to v1.133.0](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/manage-sam-cli-versions.html#manage-sam-cli-versions-upgrade) or newer and ensure any forked or derivative code is patched to incorporate the new fixes. 


### Impact

This issue is limited to the local workspace and does not affect AWS services, production environments or cross-account resources. The issue only affects local workspaces using AWS SAM CLI with container builds (--use-container), potentially allowing access to local files outside the build directory through the usage of symlinks. 



**Impacted versions:** <= AWS SAM CLI v1.132.0



### Patches

The issue has been addressed in version 1.133.0. Users should upgrade and ensure any forked or derivative code is patched to incorporate the new fixes. To retain the previous behavior and allow symlinks to resolve on the host machine, please use the explicit '-[-mount-symlinks](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-build.html#ref-sam-cli-build-options-mount-symlinks)' parameter.



### Workarounds

There is no recommended work around. Customers are advised to upgrade to version v1.133.0 or the latest version.



### References

CVE-2025-3047

---

If you have any questions or comments about this advisory we ask that you contact AWS/Amazon Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.



### Credit

We would like to thank [Kevin Backhouse](https://github.com/kevinbackhouse) with the GitHub Security Lab for collaborating on this issue through the coordinated vulnerability disclosure process.

## References
- https://github.com/aws/aws-sam-cli/security/advisories/GHSA-px37-jpqx-97q9
- https://nvd.nist.gov/vuln/detail/CVE-2025-3047
- https://github.com/aws/aws-sam-cli/pull/7865
- https://aws.amazon.com/security/security-bulletins/AWS-2025-008
- https://github.com/aws/aws-sam-cli
- https://github.com/aws/aws-sam-cli/releases/tag/v1.134.0
