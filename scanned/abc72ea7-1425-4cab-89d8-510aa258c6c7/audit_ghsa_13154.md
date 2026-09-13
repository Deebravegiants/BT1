# [M] Jetty accepts "+" prefixed value in Content-Length

## Summary
Severity: Medium
Advisory: GHSA-hmr7-m48g-48f6
CVE: CVE-2023-40167
CWE: CWE-130
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-09-14
Source: https://github.com/advisories/GHSA-hmr7-m48g-48f6
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-http` — affected >=9.0.0 <9.4.52
- Maven: `org.eclipse.jetty:jetty-http` — affected >=10.0.0 <10.0.16
- Maven: `org.eclipse.jetty:jetty-http` — affected >=11.0.0 <11.0.16
- Maven: `org.eclipse.jetty:jetty-http` — affected >=12.0.0 <12.0.1

## Details
### Impact

Jetty accepts the '+' character proceeding the content-length value in a HTTP/1 header field.  This is more permissive than allowed by the RFC and other servers routinely reject such requests with 400 responses.  There is no known exploit scenario, but it is conceivable that request smuggling could result if jetty is used in combination with a server that does not close the connection after sending such a 400 response.

### Workarounds

There is no workaround as there is no known exploit scenario.   

### Original Report 

[RFC 9110 Secion 8.6](https://www.rfc-editor.org/rfc/rfc9110#section-8.6) defined the value of Content-Length header should be a string of 0-9 digits. However we found that Jetty accepts "+" prefixed Content-Length, which could lead to potential HTTP request smuggling.

Payload:

```
 POST / HTTP/1.1
 Host: a.com
 Content-Length: +16
 Connection: close
 ​
 0123456789abcdef
```

When sending this payload to Jetty, it can successfully parse and identify the length.

When sending this payload to NGINX, Apache HTTPd or other HTTP servers/parsers, they will return 400 bad request.

This behavior can lead to HTTP request smuggling and can be leveraged to bypass WAF or IDS.

## References
- https://github.com/eclipse/jetty.project/security/advisories/GHSA-hmr7-m48g-48f6
- https://nvd.nist.gov/vuln/detail/CVE-2023-40167
- https://github.com/eclipse/jetty.project
- https://lists.debian.org/debian-lts-announce/2023/09/msg00039.html
- https://www.debian.org/security/2023/dsa-5507
- https://www.rfc-editor.org/rfc/rfc9110#section-8.6
