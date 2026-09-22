# [C] acryl-datahub missing JWT signature check

## Summary
Severity: Critical
Advisory: GHSA-r8gm-v65f-c973
CVE: CVE-2022-39366
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2022-10-31
Source: https://github.com/advisories/GHSA-r8gm-v65f-c973
Type: github-advisory

## Affected
- PyPI: `acryl-datahub` — affected >=0 <0.8.45

## Details
# Missing JWT signature check (`GHSL-2022-078`)

The [`StatelessTokenService`](https://github.com/datahub-project/datahub/blob/aa146db611e3a4ca3aa17bb740783f789d4444d3/metadata-service/auth-impl/src/main/java/com/datahub/authentication/token/StatelessTokenService.java#L30) of the DataHub metadata service (GMS) does not verify the signature of JWT tokens. This allows an attacker to connect to DataHub instances as any user if Metadata Service authentication is enabled. This vulnerability occurs because the `StatelessTokenService` of the Metadata service uses the [`parse`](https://github.com/datahub-project/datahub/blob/aa146db611e3a4ca3aa17bb740783f789d4444d3/metadata-service/auth-impl/src/main/java/com/datahub/authentication/token/StatelessTokenService.java#L134) method of `io.jsonwebtoken.JwtParser`, which does not perform a verification of the cryptographic token signature. This means that JWTs are accepted regardless of the used algorithm.

#### Impact

This issue may lead to an authentication bypass.

#### Resources

* [CodeQL: Missing JWT signature check](https://codeql.github.com/codeql-query-help/java/java-missing-jwt-signature-check/)

## References
- https://github.com/datahub-project/datahub/security/advisories/GHSA-r8gm-v65f-c973
- https://nvd.nist.gov/vuln/detail/CVE-2022-39366
- https://codeql.github.com/codeql-query-help/java/java-missing-jwt-signature-check
- https://github.com/datahub-project/datahub
- https://github.com/datahub-project/datahub/blob/aa146db611e3a4ca3aa17bb740783f789d4444d3/metadata-service/auth-impl/src/main/java/com/datahub/authentication/token/StatelessTokenService.java#L134
- https://github.com/datahub-project/datahub/blob/aa146db611e3a4ca3aa17bb740783f789d4444d3/metadata-service/auth-impl/src/main/java/com/datahub/authentication/token/StatelessTokenService.java#L30
- https://github.com/datahub-project/datahub/releases/tag/v0.8.45
