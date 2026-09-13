# [C] Improper Authentication vulnerability in Apache Solr

## Summary
Severity: Critical
Advisory: GHSA-mjvf-4h88-6xm3
CVE: CVE-2024-45216
CWE: CWE-287, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-16
Source: https://github.com/advisories/GHSA-mjvf-4h88-6xm3
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr` — affected >=5.3.0 <8.11.4
- Maven: `org.apache.solr:solr` — affected >=9.0.0 <9.7.0

## Details
Solr instances using the PKIAuthenticationPlugin, which is enabled by default when Solr Authentication is used, are vulnerable to Authentication bypass. A fake ending at the end of any Solr API URL path, will allow requests to skip Authentication while maintaining the API contract with the original URL Path. This fake ending looks like an unprotected API path, however it is stripped off internally after authentication but before API routing.


This issue affects Apache Solr: from 5.3.0 before 8.11.4, from 9.0.0 before 9.7.0.

Users are recommended to upgrade to version 9.7.0, or 8.11.4, which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45216
- https://issues.apache.org/jira/browse/SOLR-17417
- https://solr.apache.org/security.html#cve-2024-45216-apache-solr-authentication-bypass-possible-using-a-fake-url-path-ending
- http://svn.apache.org/viewvc/lucene/dev/branches/branch_4x/solr/webapp
- http://www.openwall.com/lists/oss-security/2024/10/15/8
