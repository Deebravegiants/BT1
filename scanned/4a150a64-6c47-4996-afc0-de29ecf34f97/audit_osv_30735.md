# [M] OpenTelemetry Logs source may lack authentication with some custom plugins

## Summary
Severity: Medium
Advisory: CVE-2024-55886
Aliases: GHSA-725p-63vv-v948
CVSS: 6.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:N/I:L/A:H)
Published: 2024-12-12
Source: https://osv.dev/vulnerability/CVE-2024-55886
Type: osv

## Details
OpenSearch Data Prepper is a component of the OpenSearch project that accepts, filters, transforms, enriches, and routes data at scale. A vulnerability exists in the OpenTelemetry Logs source in Data Prepper starting inversion 2.1.0 and prior to version 2.10.2 where some custom authentication plugins will not perform authentication. This allows unauthorized users to ingest OpenTelemetry Logs data under certain conditions. This vulnerability does not affect the built-in `http_basic` authentication provider in Data Prepper. Pipelines which use the `http_basic` authentication provider continue to require authentication. The vulnerability exists only for custom implementations of Data Prepper’s `GrpcAuthenticationProvider` authentication plugin which implement the `getHttpAuthenticationService()` method instead of `getAuthenticationInterceptor()`. Data Prepper 2.10.2 contains a fix for this issue. For those unable to upgrade, one may use the built-in `http_basic` authentication provider in Data Prepper and/or add an authentication proxy in front of one's Data Prepper instances running the OpenTelemetry Logs source.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55886.json
- https://github.com/opensearch-project/data-prepper/security/advisories/GHSA-725p-63vv-v948
- https://nvd.nist.gov/vuln/detail/CVE-2024-55886
