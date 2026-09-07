# [M] Cross-Site Request Forgery (CSRF) in strawberry-graphql

## Summary
Severity: Medium
Advisory: GHSA-79gp-q4wv-33fr
CVE: CVE-2024-47082
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-09-25
Source: https://github.com/advisories/GHSA-79gp-q4wv-33fr
Type: github-advisory

## Affected
- PyPI: `strawberry-graphql` — affected >=0 <0.243.0

## Details
### Impact

Multipart file upload support as defined in the [GraphQL multipart request specification](https://github.com/jaydenseric/graphql-multipart-request-spec) was enabled by default in all Strawberry HTTP view integrations. This made all Strawberry HTTP view integrations vulnerable to CSRF attacks if users did not explicitly enable CSRF preventing security mechanism for their servers.
Additionally, the Django HTTP view integration, in particular, had an exemption for Django's built-in CSRF protection (i.e., the `CsrfViewMiddleware` middleware) by default.

In affect, all Strawberry integrations were vulnerable to CSRF attacks by default.

### Patches

Version `v0.243.0` is the first `strawberry-graphql` including a patch. Check out our [documentation](https://strawberry.rocks/docs/breaking-changes/0.243.0) for additional details and upgrade instructions.

### References

- [Strawberry upgrade guide](https://strawberry.rocks/docs/breaking-changes/0.243.0)
- [Multipart Upload Security Implications](https://github.com/jaydenseric/graphql-multipart-request-spec/blob/master/readme.md#security)

### Credits

- [Thomas Grainger](https://github.com/graingert)
- [Arthur Bayr](https://github.com/speedy1991)
- [Jonathan Ehwald](https://github.com/DoctorJohn)

## References
- https://github.com/strawberry-graphql/strawberry/security/advisories/GHSA-79gp-q4wv-33fr
- https://nvd.nist.gov/vuln/detail/CVE-2024-47082
- https://github.com/strawberry-graphql/strawberry/commit/37265b230e511480a9ceace492f9f6a484be1387
- https://github.com/pypa/advisory-database/tree/main/vulns/strawberry-graphql/PYSEC-2024-171.yaml
- https://github.com/strawberry-graphql/strawberry
- https://strawberry.rocks/docs/breaking-changes/0.243.0
