# [H] SeaweedFS S3 OIDC Bearer authentication bypasses IAM role trust policy

## Summary
Severity: High
Advisory: BIT-seaweedfs-2026-77298
Aliases: CVE-2026-77298, GHSA-757h-cm9x-wprg
Ecosystem: Bitnami
Published: 2026-09-02
Source: https://osv.dev/vulnerability/BIT-seaweedfs-2026-77298
Type: osv

## Affected
- Bitnami: `seaweedfs` — affected >=0 <4.40.0

## Details
SeaweedFS is a distributed storage system for files and blobs. In versions 4.39 and earlier, the S3 API accepts an external OIDC JWT sent directly in the Authorization header and maps it to an IAM role without enforcing that role's trust policy, so a federated user can assume a role they are not permitted to hold. The standard STS AssumeRoleWithWebIdentity path rejects such a token when the role's trust policy does not trust the token's federated provider, but the direct S3 bearer path validates only the token itself and then authenticates as the mapped role and evaluates that role's attached S3 permissions. As a result, a valid OIDC user whose token would be denied the role through STS can obtain the role's S3 access, including object read, write, and delete, by presenting the raw OIDC JWT directly to the S3 API. This issue is fixed in version 4.40

## References
- https://github.com/seaweedfs/seaweedfs/commit/ac524e140a37242b2488be9dfffae918da1d4de1
- https://github.com/seaweedfs/seaweedfs/security/advisories/GHSA-757h-cm9x-wprg
- https://nvd.nist.gov/vuln/detail/CVE-2026-77298
