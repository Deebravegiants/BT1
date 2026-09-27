# [H] Jetty vulnerable to Invalid HTTP/2 requests that can lead to denial of service

## Summary
Severity: High
Advisory: GHSA-wgmr-mf83-7x4j
CVE: CVE-2022-2048
CWE: CWE-400, CWE-410
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-07
Source: https://github.com/advisories/GHSA-wgmr-mf83-7x4j
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty.http2:http2-server` — affected >=0 <9.4.47
- Maven: `org.eclipse.jetty.http2:http2-server` — affected >=10.0.0 <10.0.10
- Maven: `org.eclipse.jetty.http2:http2-server` — affected >=11.0.0 <11.0.10

## Details
### Description
Invalid HTTP/2 requests (for example, invalid URIs) are incorrectly handled by writing a blocking error response directly from the selector thread.
If the client manages to exhaust the HTTP/2 flow control window, or TCP congest the connection, the selector thread will be blocked trying to write the error response.
If this is repeated for all the selector threads, the server becomes unresponsive, causing the denial of service.

### Impact
A malicious client may render the server unresponsive.

### Patches
The fix is available in Jetty versions 9.4.47. 10.0.10, 11.0.10.

### Workarounds
No workaround available within Jetty itself.
One possible workaround is to filter the requests before sending them to Jetty (for example in a proxy)

### For more information
If you have any questions or comments about this advisory:
* Email us at security@webtide.com.

## References
- https://github.com/eclipse/jetty.project/security/advisories/GHSA-wgmr-mf83-7x4j
- https://nvd.nist.gov/vuln/detail/CVE-2022-2048
- https://github.com/eclipse/jetty.project
- https://lists.debian.org/debian-lts-announce/2022/08/msg00011.html
- https://security.netapp.com/advisory/ntap-20220901-0006
- https://www.debian.org/security/2022/dsa-5198
- http://www.openwall.com/lists/oss-security/2022/09/09/2
