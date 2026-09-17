# [H] Apache Tomcat vulnerable to information leak

## Summary
Severity: High
Advisory: GHSA-mppv-79ch-vw6q
CVE: CVE-2023-34981
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-21
Source: https://github.com/advisories/GHSA-mppv-79ch-vw6q
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M5 <11.0.0-M6
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.8 <10.1.9
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.74 <9.0.75
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=8.5.88 <8.5.89

## Details
A regression in the fix for bug 66512 in Apache Tomcat 11.0.0-M5, 10.1.8, 9.0.74 and 8.5.88 meant that, if a response did not include any HTTP headers no AJP SEND_HEADERS message would be sent for the response which in turn meant that at least one AJP proxy (mod_proxy_ajp) would use the response headers from the previous request leading to an information leak.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34981
- https://github.com/apache/tomcat/commit/2214c8030522aa9b2a367dfa5d9acff1a03666ae
- https://github.com/apache/tomcat/commit/2f0ca2378415f4cf0748f4bc8fa955f41f803fa5
- https://github.com/apache/tomcat/commit/739c7381aed22b7636351caf885ddc519ab6b442
- https://github.com/apache/tomcat/commit/f0742f47b98aca943097f7f88e0d1163f57527e3
- https://bz.apache.org/bugzilla/show_bug.cgi?id=66512
- https://bz.apache.org/bugzilla/show_bug.cgi?id=66591
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/j1ksjh9m9gx1q60rtk1sbzmxhvj5h5qz
- https://security.netapp.com/advisory/ntap-20230714-0003
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-11.html
- https://tomcat.apache.org/security-8.html
- https://tomcat.apache.org/security-9.html
