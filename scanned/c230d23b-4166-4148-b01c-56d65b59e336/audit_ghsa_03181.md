# [C] Incorrect Authorization in Apache Solr

## Summary
Severity: Critical
Advisory: GHSA-vf7p-j8x6-xvwp
CVE: CVE-2021-29943
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-vf7p-j8x6-xvwp
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-parent` — affected >=0 <8.8.2

## Details
When using ConfigurableInternodeAuthHadoopPlugin for authentication, Apache Solr versions prior to 8.8.2 would forward/proxy distributed requests using server credentials instead of original client credentials. This would result in incorrect authorization resolution on the receiving hosts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29943
- https://lists.apache.org/thread.html/r91dd0ff556e0c9aab4c92852e0e540c59d4633718ce12881558cf44d%40%3Cusers.solr.apache.org%3E
- https://security.netapp.com/advisory/ntap-20210604-0009
