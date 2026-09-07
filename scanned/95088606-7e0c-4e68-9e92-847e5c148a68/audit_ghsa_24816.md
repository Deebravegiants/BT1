# [M] Apache Rave information disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-428j-q447-47rw
CVE: CVE-2013-1814
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-428j-q447-47rw
Type: github-advisory

## Affected
- Maven: `org.apache.rave:rave-core` — affected >=0.11 <0.20.1
- Maven: `org.apache.rave:rave-web` — affected >=0.11 <0.20.1
- Maven: `org.apache.rave:rave-portal-resources` — affected >=0.11 <0.20.1

## Details
The users/get program in the User RPC API in Apache Rave 0.11 through 0.20 allows remote authenticated users to obtain sensitive information about all user accounts via the offset parameter, as demonstrated by discovering password hashes in the password field of a response.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1814
- https://github.com/apache/rave/commit/546edbaacfcb7b3fcc81aafe37a5c58e401b66c6
- https://github.com/apache/rave
- https://web.archive.org/web/20130512040207/http://archives.neohapsis.com/archives/bugtraq/2013-03/0078.html
- http://archives.neohapsis.com/archives/bugtraq/2013-03/0078.html
- http://www.exploit-db.com/exploits/24744
