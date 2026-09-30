# [C] SQL Query Validation Bypass in OpenSearch Direct Query

## Summary
Severity: Critical
Advisory: CVE-2026-18428
Aliases: GHSA-g4jr-343c-fvjm
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-18428
Type: osv

## Details
A SQL query validation bypass in the Flint extension query handler in the OpenSearch SQL plugin allows a remote authenticated actor with async query access to execute arbitrary code on Apache Spark workers by sending a crafted SQL query to the direct query endpoint.

## References
- https://aws.amazon.com/security/security-bulletins/2026-081-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18428.json
- https://github.com/opensearch-project/sql/security/advisories/GHSA-g4jr-343c-fvjm
- https://nvd.nist.gov/vuln/detail/CVE-2026-18428
- https://docs.aws.amazon.com/opensearch-service/latest/developerguide/service-software.html
- https://opensearch.org/artifacts/by-version/?_gl=1*d14pqp*_up*MQ..*_ga*Nzc5NTAxNzM2LjE3ODM1NTA2NDA.*_ga_BQV14XK08F*czE3ODM1NTA2NDAkbzEkZzEkdDE3ODM1NTA3MTQkajU2JGwwJGg3NTc4ODY0OTM.#release-2-19-6
- https://opensearch.org/artifacts/by-version/?_gl=1*d14pqp*_up*MQ..*_ga*Nzc5NTAxNzM2LjE3ODM1NTA2NDA.*_ga_BQV14XK08F*czE3ODM1NTA2NDAkbzEkZzEkdDE3ODM1NTA3MTQkajU2JGwwJGg3NTc4ODY0OTM.#release-3-7-0
