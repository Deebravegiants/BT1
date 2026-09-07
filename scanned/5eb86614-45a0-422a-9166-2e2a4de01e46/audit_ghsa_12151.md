# [C] MinIO has JWT Algorithm Confusion in OIDC Authentication

## Summary
Severity: Critical
Advisory: GHSA-5cx5-wh4m-82fh
CVE: CVE-2026-33322
CWE: CWE-287, CWE-327
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-5cx5-wh4m-82fh
Type: github-advisory

## Affected
- Go: `github.com/minio/minio` — affected >=0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

A JWT algorithm confusion vulnerability in MinIO's OpenID Connect authentication allows an attacker who knows the OIDC `ClientSecret` to forge arbitrary identity tokens and obtain S3 credentials with any policy, including `consoleAdmin`.

An attacker with knowledge of the OIDC `ClientSecret` can:

- Impersonate any user identity
- Obtain S3 credentials with any IAM policy, including `consoleAdmin`
- Access, modify, or delete any data in the MinIO deployment

The attack is deterministic (100% success rate, no race conditions).

#### Attack Prerequisites

The attacker must know the OIDC `ClientSecret`. While this is a shared credential (not a private key), it is more accessible than commonly assumed:

- CVE-2023-28432 previously leaked environment variables including `MINIO_IDENTITY_OPENID_CLIENT_SECRET`
- Client secrets are often present in frontend OAuth configurations, mobile app bundles, CI/CD pipelines, and shared configuration files
- In many organizations, the client secret is accessible to operators and engineers who should not be able to forge arbitrary identities


#### Affected Versions

All MinIO releases from `RELEASE.2022-11-08T05-27-07Z` through the final release of the `minio/minio` open-source project.

### Patches

**Fixed in:** MinIO AIStor `RELEASE.2026-03-17T21-25-16Z`

## Downloads

### Binary Downloads

| Platform | Architecture | Download                                                                    |
| -------- | ------------ | --------------------------------------------------------------------------- |
| Linux    | amd64        | [minio](https://dl.min.io/aistor/minio/release/linux-amd64/minio)           |
| Linux    | arm64        | [minio](https://dl.min.io/aistor/minio/release/linux-arm64/minio)           |
| macOS    | arm64        | [minio](https://dl.min.io/aistor/minio/release/darwin-arm64/minio)          |
| macOS    | amd64        | [minio](https://dl.min.io/aistor/minio/release/darwin-amd64/minio)          |
| Windows  | amd64        | [minio.exe](https://dl.min.io/aistor/minio/release/windows-amd64/minio.exe) |

### FIPS Binaries

| Platform | Architecture | Download                                                                    |
| -------- | ------------ | --------------------------------------------------------------------------- |
| Linux    | amd64        | [minio.fips](https://dl.min.io/aistor/minio/release/linux-amd64/minio.fips) |
| Linux    | arm64        | [minio.fips](https://dl.min.io/aistor/minio/release/linux-arm64/minio.fips) |

### Package Downloads

| Format | Architecture | Download                                                                                                                            |
| ------ | ------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| DEB    | amd64        | [minio_20260317212516.0.0_amd64.deb](https://dl.min.io/aistor/minio/release/linux-amd64/minio_20260317212516.0.0_amd64.deb)         |
| DEB    | arm64        | [minio_20260317212516.0.0_arm64.deb](https://dl.min.io/aistor/minio/release/linux-arm64/minio_20260317212516.0.0_arm64.deb)         |
| RPM    | amd64        | [minio-20260317212516.0.0-1.x86_64.rpm](https://dl.min.io/aistor/minio/release/linux-amd64/minio-20260317212516.0.0-1.x86_64.rpm)   |
| RPM    | arm64        | [minio-20260317212516.0.0-1.aarch64.rpm](https://dl.min.io/aistor/minio/release/linux-arm64/minio-20260317212516.0.0-1.aarch64.rpm) |

### Container Images

```bash
# Standard
docker pull quay.io/minio/aistor/minio:RELEASE.2026-03-17T21-25-16Z
podman pull quay.io/minio/aistor/minio:RELEASE.2026-03-17T21-25-16Z

# FIPS
docker pull quay.io/minio/aistor/minio:RELEASE.2026-03-17T21-25-16Z.fips
podman pull quay.io/minio/aistor/minio:RELEASE.2026-03-17T21-25-16Z.fips
```

### Homebrew (macOS)

```bash
brew install minio/aistor/minio
```

### Workarounds

- [Users of the open-source `minio/minio` project should upgrade to MinIO AIStor `RELEASE.2026-03-17T21-25-16Z` or later.](https://docs.min.io/enterprise/aistor-object-store/upgrade-aistor-server/community-edition/)
- As a workaround, ensure that the OIDC `ClientSecret` is treated as a highly sensitive credential and is not exposed to untrusted parties.

## References
- https://github.com/minio/minio/security/advisories/GHSA-5cx5-wh4m-82fh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33322
- https://github.com/minio/minio
