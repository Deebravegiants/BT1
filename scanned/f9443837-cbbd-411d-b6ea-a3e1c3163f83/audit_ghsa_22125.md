# [H] Apache Solr insecure inter-node communication

## Summary
Severity: High
Advisory: GHSA-c82r-qg3w-q5mv
CVE: CVE-2017-7660
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-c82r-qg3w-q5mv
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-core` — affected >=5.3.0 <5.5.5
- Maven: `org.apache.solr:solr-core` — affected >=6.0.0 <6.6.0

## Details
Apache Solr uses a PKI based mechanism to secure inter-node communication when security is enabled. It is possible to create a specially crafted node name that does not exist as part of the cluster and point it to a malicious node. This can trick the nodes in cluster to believe that the malicious node is a member of the cluster. So, if Solr users have enabled BasicAuth authentication mechanism using the BasicAuthPlugin or if the user has implemented a custom Authentication plugin, which does not implement either "HttpClientInterceptorPlugin" or "HttpClientBuilderPlugin", his/her servers are vulnerable to this attack. Users who only use SSL without basic authentication or those who use Kerberos are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7660
- https://issues.apache.org/jira/browse/SOLR-10624
- https://lists.apache.org/thread/o0g7vpz5sz4yy0pyf1z94vkpv40x6h44
- https://security.netapp.com/advisory/ntap-20181127-0003
