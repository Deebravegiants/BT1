# [M] Generation of Error Message Containing Sensitive Information in RESTEasy client

## Summary
Severity: Medium
Advisory: GHSA-hr32-mgpm-qf2f
CVE: CVE-2020-25633
CWE: CWE-209
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-06-03
Source: https://github.com/advisories/GHSA-hr32-mgpm-qf2f
Type: github-advisory

## Affected
- Maven: `org.jboss.resteasy:resteasy-client` — affected >=4.0.0 <4.5.7.Final
- Maven: `org.jboss.resteasy:resteasy-client-microprofile` — affected >=4.0.0 <4.5.7.Final
- Maven: `org.jboss.resteasy:resteasy-client` — affected >=0 <3.14.0.Final
- Maven: `org.jboss.resteasy:resteasy-client-microprofile` — affected >=0 <3.14.0.Final

## Details
A flaw was found in RESTEasy client in all versions of RESTEasy up to 4.5.6.Final. It may allow client users to obtain the server's potentially sensitive information when the server got WebApplicationException from the RESTEasy client call. The highest threat from this vulnerability is to data confidentiality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25633
- https://github.com/resteasy/Resteasy/pull/2665/commits/13c808b5967242eec1e877edbc0014a84dcd6eb0
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-25633
- https://issues.redhat.com/browse/RESTEASY-2820
