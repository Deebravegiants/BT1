# [H] Minio Information Disclosure in Cluster Deployment

## Summary
Severity: High
Advisory: BIT-minio-2023-28432
Aliases: CVE-2023-28432, GHSA-6xvq-wj2x-3h3q
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-minio-2023-28432
Type: osv

## Affected
- Bitnami: `minio` — affected >=2019.12.17 <2023.03.20

## Details
Minio is a Multi-Cloud Object Storage framework. In a cluster deployment starting with RELEASE.2019-12-17T23-16-33Z and prior to RELEASE.2023-03-20T20-16-18Z, MinIO returns all environment variables, including `MINIO_SECRET_KEY`
and `MINIO_ROOT_PASSWORD`, resulting in information disclosure. All users of distributed deployment are impacted. All users are advised to upgrade to RELEASE.2023-03-20T20-16-18Z.

## References
- https://github.com/minio/minio/releases/tag/RELEASE.2023-03-20T20-16-18Z
- https://github.com/minio/minio/security/advisories/GHSA-6xvq-wj2x-3h3q
- https://twitter.com/Andrew___Morris/status/1639325397241278464
- https://viz.greynoise.io/tag/minio-information-disclosure-attempt
- https://www.greynoise.io/blog/openai-minio-and-why-you-should-always-use-docker-cli-scan-to-keep-your-supply-chain-clean
- https://nvd.nist.gov/vuln/detail/CVE-2023-28432
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2023-28432
