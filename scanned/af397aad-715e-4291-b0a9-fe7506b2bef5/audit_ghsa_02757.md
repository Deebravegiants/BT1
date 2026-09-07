# [M] API information disclosure flaw in Elasticsearch

## Summary
Severity: Medium
Advisory: GHSA-62ww-4p3p-7fhj
CVE: CVE-2021-22135
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-07-02
Source: https://github.com/advisories/GHSA-62ww-4p3p-7fhj
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.0.0 <7.11.2
- Maven: `org.elasticsearch:elasticsearch` — affected >=0 <6.8.15

## Details
Elasticsearch versions before 7.11.2 and 6.8.15 contain a document disclosure flaw was found in the Elasticsearch suggester and profile API when Document and Field Level Security are enabled. The suggester and profile API are normally disabled for an index when document level security is enabled on the index. Certain queries are able to enable the profiler and suggester which could lead to disclosing the existence of documents and fields the attacker should not be able to view.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22135
- https://discuss.elastic.co/t/elastic-stack-7-12-0-and-6-8-15-security-update/268125
- https://security.netapp.com/advisory/ntap-20210625-0003
