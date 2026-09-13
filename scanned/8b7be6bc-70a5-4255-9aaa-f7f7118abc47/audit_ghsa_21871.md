# [C] Apache Cassandra vulnerable to Code Injection due to unsafe configuration

## Summary
Severity: Critical
Advisory: GHSA-8ffc-79xg-29w8
CVE: CVE-2021-44521
CWE: CWE-732, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-8ffc-79xg-29w8
Type: github-advisory

## Affected
- Maven: `org.apache.cassandra:cassandra-all` — affected >=0 <3.0.26
- Maven: `org.apache.cassandra:cassandra-all` — affected >=3.11.0 <3.11.12
- Maven: `org.apache.cassandra:cassandra-all` — affected >=4.0.0 <4.0.2

## Details
When running Apache Cassandra with the following configuration: enable_user_defined_functions: true enable_scripted_user_defined_functions: true enable_user_defined_functions_threads: false it is possible for an attacker to execute arbitrary code on the host. The attacker would need to have enough permissions to create user defined functions in the cluster to be able to exploit this. Note that this configuration is documented as unsafe, and will continue to be considered unsafe after this CVE.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44521
- https://github.com/apache/cassandra
- https://issues.apache.org/jira/browse/CASSANDRA-17352
- https://jfrog.com/blog/cve-2021-44521-exploiting-apache-cassandra-user-defined-functions-for-remote-code-execution
- https://lists.apache.org/thread/y4nb9s4co34j8hdfmrshyl09lokm7356
- https://security.netapp.com/advisory/ntap-20220225-0001
- http://www.openwall.com/lists/oss-security/2022/02/11/4
