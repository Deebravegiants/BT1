# [M] Trivy possibly leaks registry credential when scanning images from malicious registries

## Summary
Severity: Medium
Advisory: GHSA-xcq4-m2r3-cmrj
CVE: CVE-2024-35192
CWE: CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-xcq4-m2r3-cmrj
Type: github-advisory

## Affected
- Go: `github.com/aquasecurity/trivy` — affected >=0 <0.51.2

## Details
## Impact
If a malicious actor is able to trigger Trivy to scan container images from a crafted malicious registry, it could result in the leakage of credentials for legitimate registries such as AWS Elastic Container Registry (ECR), Google Cloud Artifact/Container Registry, or Azure Container Registry (ACR). These tokens can then be used to push/pull images from those registries to which the identity/user running Trivy has access.

Taking AWS as an example, the leakage only occurs when Trivy is able to transparently obtain registry credentials from the default [credential provider chain](https://aws.github.io/aws-sdk-go-v2/docs/configuring-sdk/#specifying-credentials). You are affected if Trivy is executed in any of the following situations:

- The environment variables contain static AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN) that have access to ECR.
- Within a Pod running on an EKS cluster that has been assigned a role with access to ECR using an [IAM Roles for Service Accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html) (IRSA) annotation.
- etc.

You are not affected if the default credential provider chain is unable to obtain valid credentials. The same applies to GCP and Azure.

## Workarounds
If you are using Trivy v0.51.2 or later, you are not affected. If you are using Trivy v0.51.1 or prior, you should ensure you only scan images from trusted registries.

This vulnerability only applies when scanning container images directly from a registry. If you use Docker, containerd or other runtime to pull images locally and scan them with Trivy, you are not affected. To enforce this behavior, you can use the `--image-src` flag to select which sources you trust.

## References
- https://github.com/aquasecurity/trivy/security/advisories/GHSA-xcq4-m2r3-cmrj
- https://nvd.nist.gov/vuln/detail/CVE-2024-35192
- https://github.com/aquasecurity/trivy/commit/e7f14f729de259551203f313e57d2d9d3aa2ff87
- https://github.com/aquasecurity/trivy
