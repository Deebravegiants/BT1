# [M] Elasticsearch allows insertion of sensitive information into log files when using deprecated URIs

## Summary
Severity: Medium
Advisory: GHSA-99pc-69q9-jxf2
CVE: CVE-2023-31417
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-26
Source: https://github.com/advisories/GHSA-99pc-69q9-jxf2
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.0.0 <7.17.13
- Maven: `org.elasticsearch:elasticsearch` — affected >=8.0.0 <8.9.2

## Details
Elasticsearch generally filters out sensitive information and credentials before logging to the audit log. It was found that this filtering was not applied when requests to Elasticsearch use certain deprecated URIs for APIs. The impact of this flaw is that sensitive information such as passwords and tokens might be printed in cleartext in Elasticsearch audit logs. Note that audit logging is disabled by default and needs to be explicitly enabled and even when audit logging is enabled, request bodies that could contain sensitive information are not printed to the audit log unless explicitly configured.

The `_xpack/security` APIs have been deprecated in Elasticsearch 7.x and were entirely removed in 8.0.0 and later. The only way for a client to use them in Elasticsearch 8.0.0 and later is to provide the `Accept: application/json; compatible-with=7` header. Elasticsearch official clients do not use these deprecated APIs.

The list of affected, deprecated APIs, is the following:

`POST /_xpack/security/user/{username}`
`PUT /_xpack/security/user/{username}`
`PUT /_xpack/security/user/{username}/_password`
`POST /_xpack/security/user/{username}/_password`
`PUT /_xpack/security/user/_password`
`POST /_xpack/security/user/_password`
`POST /_xpack/security/oauth2/token`
`DELETE /_xpack/security/oauth2/token`
`POST /_xpack/security/saml/authenticate`

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31417
- https://discuss.elastic.co/t/elasticsearch-8-9-2-and-7-17-13-security-update/342479
- https://security.netapp.com/advisory/ntap-20231130-0006
- https://www.elastic.co/community/security
