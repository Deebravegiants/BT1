# [H] CVE-2018-11783

## Summary
Severity: High
Advisory: CVE-2018-11783
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-03-07
Source: https://osv.dev/vulnerability/CVE-2018-11783
Type: osv

## Details
sslheaders plugin extracts information from the client certificate and sets headers in the request based on the configuration of the plugin. The plugin doesn't strip the headers from the request in some scenarios. This problem was discovered in versions 6.0.0 to 6.0.3, 7.0.0 to 7.1.5, and 8.0.0 to 8.0.1.

## References
- https://lists.apache.org/thread.html/4f102f943935476732fb1fb653d687c7b69d29d9792f0d6cf72c505e%40%3Cannounce.trafficserver.apache.org%3E
- http://www.securityfocus.com/bid/107032
