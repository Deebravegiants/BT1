# [H] Multiple cryptographic issues in Python oic

## Summary
Severity: High
Advisory: GHSA-4fjv-pmhg-3rfg
CVE: CVE-2020-26244
CWE: CWE-325, CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-12-04
Source: https://github.com/advisories/GHSA-4fjv-pmhg-3rfg
Type: github-advisory

## Affected
- PyPI: `oic` — affected >=0 <1.2.1

## Details
### Impact
* Client implementations using this library

### Issues
1) The IdToken signature algorithm was not checked automatically, but only if the expected algorithm was passed in as a kwarg.
2) JWA `none` algorithm was allowed in all flows.
3) `oic.consumer.Consumer.parse_authz` returns an unverified IdToken. The verification of the token was left to the discretion of the implementator.
4) `iat` claim was not checked for sanity (i.e. it could be in the future)

### Patches
1) IdToken signature is now always checked.
2) JWA `none` algorithm is now allowed only if using the `response_type` `code`
3) IdToken verification is now done automatically.
4) `iat` claim is now checked for sanity.

## References
- https://github.com/OpenIDC/pyoidc/security/advisories/GHSA-4fjv-pmhg-3rfg
- https://nvd.nist.gov/vuln/detail/CVE-2020-26244
- https://github.com/OpenIDC/pyoidc/commit/62f8d753fa17c8b1f29f8be639cf0b33afb02498
- https://github.com/OpenIDC/pyoidc
- https://github.com/OpenIDC/pyoidc/releases/tag/1.2.1
- https://github.com/pypa/advisory-database/tree/main/vulns/oic/PYSEC-2020-69.yaml
- https://pypi.org/project/oic
