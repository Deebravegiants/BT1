# [M] Exposure of Sensitive Information to an Unauthorized Actor in Apache HttpClient

## Summary
Severity: Medium
Advisory: GHSA-gw85-4gmf-m7rh
CVE: CVE-2011-1498
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-gw85-4gmf-m7rh
Type: github-advisory

## Affected
- Maven: `org.apache.httpcomponents:httpclient` — affected >=4.0.0 <4.1.1

## Details
Apache HttpClient 4.x before 4.1.1 in Apache HttpComponents, when used with an authenticating proxy server, sends the Proxy-Authorization header to the origin server, which allows remote web servers to obtain sensitive information by logging this header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-1498
- https://github.com/apache/httpcomponents-client/commit/a572756592c969affd0ce87885724e74839176fb
- https://bugzilla.redhat.com/show_bug.cgi?id=709531
- https://github.com/apache/httpcomponents-client
- https://issues.apache.org/jira/browse/HTTPCLIENT-1061
- http://lists.fedoraproject.org/pipermail/package-announce/2011-June/061440.html
- http://marc.info/?l=httpclient-users&m=129853896315461&w=2
- http://marc.info/?l=httpclient-users&m=129856318011586&w=2
- http://marc.info/?l=httpclient-users&m=129857589129183&w=2
- http://marc.info/?l=httpclient-users&m=129858274406594&w=2
- http://marc.info/?l=httpclient-users&m=129858299106950&w=2
- http://openwall.com/lists/oss-security/2011/04/07/7
- http://openwall.com/lists/oss-security/2011/04/08/1
- http://securityreason.com/securityalert/8298
