# [M] CVE-2018-8003

## Summary
Severity: Medium
Advisory: CVE-2018-8003
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-05-03
Source: https://osv.dev/vulnerability/CVE-2018-8003
Type: osv

## Details
Apache Ambari, versions 1.4.0 to 2.6.1, is susceptible to a directory traversal attack allowing an unauthenticated user to craft an HTTP request which provides read-only access to any file on the filesystem of the host the Ambari Server runs on that is accessible by the user the Ambari Server is running as. Direct network access to the Ambari Server is required to issue this request, and those Ambari Servers that are protected behind a firewall, or in a restricted network zone are at less risk of being affected by this issue.

## References
- http://www.securityfocus.com/bid/104161
- https://cwiki.apache.org/confluence/display/AMBARI/Ambari+Vulnerabilities#AmbariVulnerabilities-CVE-2018-8003
