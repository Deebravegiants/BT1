# [M] NanoHTTPD Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pr5m-4w22-8483
CVE: CVE-2020-13697
CWE: CWE-79
Ecosystem: Maven
Published: 2021-02-25
Source: https://github.com/advisories/GHSA-pr5m-4w22-8483
Type: github-advisory

## Affected
- Maven: `org.nanohttpd:nanohttpd-nanolets` — affected >=0

## Details
An issue was discovered in RouterNanoHTTPD.java in NanoHTTPD through 2.3.1. The GeneralHandler class implements a basic GET handler that prints debug information as an HTML page. Any web server that extends this class without implementing its own GET handler is vulnerable to reflected XSS, because the GeneralHandler GET handler prints user input passed through the query string without any sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13697
- https://github.com/NanoHttpd/nanohttpd
- https://github.com/NanoHttpd/nanohttpd/blob/efb2ebf85a2b06f7c508aba9eaad5377e3a01e81/nanolets/pom.xml
- https://github.com/NanoHttpd/nanohttpd/blob/efb2ebf85a2b06f7c508aba9eaad5377e3a01e81/nanolets/src/main/java/org/nanohttpd/router/RouterNanoHTTPD.java
- https://www.vdoo.com/advisories/#CVE-2020-13697
