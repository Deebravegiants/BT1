# [M] AWS CDK EKS overly permissive trust policies

## Summary
Severity: Medium
Advisory: GHSA-rx28-r23p-2qc3
CVE: CVE-2023-35165
CWE: CWE-266, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-19
Source: https://github.com/advisories/GHSA-rx28-r23p-2qc3
Type: github-advisory

## Affected
- npm: `aws-cdk-lib` — affected >=2.0.0 <2.80.0
- npm: `@aws-cdk/aws-eks` — affected >=1.57.0 <1.202.0

## Details
If you are using the `eks.Cluster` or `eks.FargateCluster` construct we need you to take action. Other users are not affected and can stop reading.

### Impact 

The AWS Cloud Development Kit (CDK) allows for the definition of Amazon Elastic Container Service for Kubernetes (EKS) clusters. `eks.Cluster` and `eks.FargateCluster` constructs create two roles that have an overly permissive trust policy. 
 
The first, referred to as the _CreationRole_, is used by lambda handlers to create the cluster and deploy Kubernetes resources (e.g `KubernetesManifest`, `HelmChart`, ...) onto it. Users with CDK version higher or equal to  [1.62.0](https://github.com/aws/aws-cdk/releases/tag/v1.62.0) (including v2 users) will be affected.
 
The second, referred to as the _default MastersRole_, is provisioned only if the `mastersRole` property isn't provided and has permissions to execute `kubectl` commands on the cluster. Users with CDK version higher or equal to [1.57.0](https://github.com/aws/aws-cdk/releases/tag/v1.57.0) (including v2 users) will be affected.
 
Both these roles use the account root principal in their trust policy, which allows any identity in the account with the appropriate `sts:AssumeRole `permissions to assume it. For example, this can happen if another role in your account has `sts:AssumeRole` permissions on `Resource: "*"`.

#### CreationRole 

Users with CDK version higher or equal to [1.62.0](https://github.com/aws/aws-cdk/releases/tag/v1.62.0) (including v2 users). The role in question can be located in the IAM console. It will have the following name pattern: 

```console 
*-ClusterCreationRole-* 
```

#### MastersRole 

Users with CDK version higher or equal to [1.57.0](https://github.com/aws/aws-cdk/releases/tag/v1.57.0) (including v2 users) that are not specifying the `mastersRole` property. The role in question can be located in the IAM console. It will have the following name pattern: 

```console
*-MastersRole-*
```

### Patches 

The issue has been fixed in versions [v1.202.0](https://github.com/aws/aws-cdk/releases/tag/v1.202.0), [v2.80.0](https://github.com/aws/aws-cdk/releases/tag/v2.80.0). We recommend you upgrade to a fixed version as soon as possible. See [Managing Dependencies](https://docs.aws.amazon.com/cdk/v2/guide/manage-dependencies.html) in the CDK Developer Guide for instructions on how to do this.  
 
The new versions no longer use the account root principal. Instead, they restrict the trust policy to the specific roles of lambda handlers that need it. This introduces some breaking changes that might require you to perform code changes. Refer to https://github.com/aws/aws-cdk/issues/25674 for a detailed discussion of options. 

### Workarounds 

#### CreationRole 

There is no workaround available for CreationRole. 

#### MastersRole 

To avoid creating the _default MastersRole_, use the `mastersRole` property to explicitly provide a role. For example: 

```ts 
new eks.Cluster(this, 'Cluster', { 
  ... 
  mastersRole: iam.Role.fromRoleArn(this, 'Admin', 'arn:aws:iam::xxx:role/Admin') 
}); 
```

### References

[https://github.com/aws/aws-cdk/issues/25674](https://github.com/aws/aws-cdk/issues/25674)

If you have any questions or comments about this advisory we ask that you contact AWS/Amazon Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/aws-cdk/security/advisories/GHSA-rx28-r23p-2qc3
- https://nvd.nist.gov/vuln/detail/CVE-2023-35165
- https://github.com/aws/aws-cdk/issues/25674
- https://github.com/aws/aws-cdk
