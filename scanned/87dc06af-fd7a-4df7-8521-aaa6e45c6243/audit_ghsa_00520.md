# [M] Moderate severity vulnerability that affects org.postgresql:pgjdbc-aggregate

## Summary
Severity: Medium
Advisory: GHSA-568q-9fw5-28wf
CVE: CVE-2018-10936
CWE: CWE-297
Ecosystem: Maven
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-568q-9fw5-28wf
Type: github-advisory

## Affected
- Maven: `org.postgresql:pgjdbc-aggregate` — affected >=0 <42.2.5

## Details
A weakness was found in postgresql-jdbc before version 42.2.5. It was possible to provide an SSL Factory and not check the host name if a host name verifier was not provided to the driver. This could lead to a condition where a man-in-the-middle attacker could masquerade as a trusted server by providing a certificate for the wrong host, as long as it was signed by a trusted CA.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10936
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10936
- https://github.com/advisories/GHSA-568q-9fw5-28wf
- https://lists.apache.org/thread.html/9317fd092b257a0815434b116a8af8daea6e920b6673f4fd5583d5fe@%3Ccommits.druid.apache.org%3E
- https://www.postgresql.org/about/news/1883
- http://www.securityfocus.com/bid/105220
