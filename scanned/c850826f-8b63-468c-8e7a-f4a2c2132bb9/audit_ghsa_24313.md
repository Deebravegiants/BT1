# [H] Improper Input Validation in RESTEasy

## Summary
Severity: High
Advisory: GHSA-63cq-ppq8-cw6g
CVE: CVE-2020-1695
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-63cq-ppq8-cw6g
Type: github-advisory

## Affected
- Maven: `org.jboss.resteasy:resteasy-client` — affected >=4.0.0 <4.6.0
- Maven: `org.jboss.resteasy:resteasy-client` — affected >=3.0.0 <3.12.0

## Details
A flaw was found in all resteasy 3.x.x versions prior to 3.12.0.Final and all resteasy 4.x.x versions prior to 4.6.0.Final, where an improper input validation results in returning an illegal header that integrates into the server's response. This flaw may result in an injection, which leads to unexpected behavior when the HTTP response is constructed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1695
- https://github.com/resteasy/Resteasy/commit/88ba8537f2e8d465c7031d352bf9bb25526ce475
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1695
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IJDMT443YZWCBS5NS76XZ7TL3GK7BXHL
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RX22C6I56BJUER76IIPYHGZIWBQIU3CQ
