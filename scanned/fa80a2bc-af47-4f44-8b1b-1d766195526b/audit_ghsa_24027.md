# [H] Apache Solr Kerberos delegation token functionality flaws

## Summary
Severity: High
Advisory: GHSA-f553-j2gv-g5r9
CVE: CVE-2017-9803
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-f553-j2gv-g5r9
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-core` — affected >=6.2.0 <6.6.1

## Details
Apache Solr's Kerberos plugin can be configured to use delegation tokens, which allows an application to reuse the authentication of an end-user or another application. There are two issues with this functionality (when using SecurityAwareZkACLProvider type of ACL provider e.g. SaslZkACLProvider). Firstly, access to the security configuration can be leaked to users other than the solr super user. Secondly, malicious users can exploit this leaked configuration for privilege escalation to further expose/modify private data and/or disrupt operations in the Solr cluster. The vulnerability is fixed from Apache Solr 6.6.1 onwards.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9803
- https://issues.apache.org/jira/browse/SOLR-11184
- https://lists.apache.org/thread/f4rbt657n9x4kb74k1txhcojof5dzol5
