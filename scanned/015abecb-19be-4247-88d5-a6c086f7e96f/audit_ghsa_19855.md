# [M] AWS SAM CLI Path Traversal allows file copy to local cache

## Summary
Severity: Medium
Advisory: GHSA-pp64-wj43-xqcr
CVE: CVE-2025-3048
CWE: CWE-22, CWE-61
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-31
Source: https://github.com/advisories/GHSA-pp64-wj43-xqcr
Type: github-advisory

## Affected
- PyPI: `aws-sam-cli` — affected >=0 <1.134.0

## Details
### Summary

The [AWS Serverless Application Model Command Line Interface (AWS SAM CLI)](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/using-sam-cli.html) is an open-source CLI tool that helps Lambda developers to build and develop Lambda applications locally on their computers using Docker.

After completing a build with AWS SAM CLI which include symlinks, the content of those symlinks are copied to the cache of the local workspace as regular files or directories. As a result, a user who does not have access to those symlinks outside of the Docker container would now have access via the local workspace.

Users should [upgrade to v1.134.0 or newer](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/manage-sam-cli-versions.html#manage-sam-cli-versions-upgrade) and ensure any forked or derivative code is patched to incorporate the new fixes. After upgrading, users must re-build their applications using the `sam build --use-container` to update the symlinks.



### Impact

The issue is limited to the local workspace and does not affect AWS services, production environments or cross-account resources. The issue only affects workspaces using the AWS SAM CLI with container builds (--use-container), potentially allowing access to content of linked files in the SAM CLI cache.



**Impacted versions:** <= AWS SAM CLI v1.133.0



### Patches

The patches are included in AWS SAM CLI  version to v1.134.0 and newer. Users should upgrade and ensure any forked or derivative code is patched to incorporate the new fixes. After upgrading, users must re-build their applications using the `sam build --use-container` to update the symlinks



### Workarounds

There is no recommended work around. Customers are advised to upgrade to version v1.134.0 or the latest version.



### References

CVE-2025-3048

---

If you have any questions or comments about this advisory we ask that you contact AWS/Amazon Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.



### Credit

We would like to thank [Kevin Backhouse](https://github.com/kevinbackhouse) with the GitHub Security Lab for collaborating on this issue through the coordinated vulnerability disclosure process.

## References
- https://github.com/aws/aws-sam-cli/security/advisories/GHSA-pp64-wj43-xqcr
- https://nvd.nist.gov/vuln/detail/CVE-2025-3048
- https://github.com/aws/aws-sam-cli/pull/7890
- https://aws.amazon.com/security/security-bulletins/AWS-2025-008
- https://github.com/aws/aws-sam-cli
- https://github.com/aws/aws-sam-cli/releases/tag/v1.134.0
