# [M] Minio vulnerable to denial of access by an admin privileged user for root credential

## Summary
Severity: Medium
Advisory: BIT-minio-2023-27589
Aliases: CVE-2023-27589, GHSA-9wfv-wmf7-6753
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-minio-2023-27589
Type: osv

## Affected
- Bitnami: `minio` — affected >=2020.12.23 <2023.03.13

## Details
Minio is a Multi-Cloud Object Storage framework. Starting with RELEASE.2020-12-23T02-24-12Z and prior to RELEASE.2023-03-13T19-46-17Z, a user with `consoleAdmin` permissions can potentially create a user that matches the root credential `accessKey`. Once this user is created successfully, the root credential ceases to work appropriately. The issue is patched in RELEASE.2023-03-13T19-46-17Z. There are ways to work around this via adding higher privileges to the disabled root user via `mc admin policy set`.

## References
- https://github.com/minio/minio/pull/16803
- https://github.com/minio/minio/security/advisories/GHSA-9wfv-wmf7-6753
- https://nvd.nist.gov/vuln/detail/CVE-2023-27589
