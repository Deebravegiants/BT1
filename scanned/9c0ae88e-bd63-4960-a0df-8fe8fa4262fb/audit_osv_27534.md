# [H] Apache bRPC: HTTP request smuggling vulnerability

## Summary
Severity: High
Advisory: CVE-2024-23452
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-02-08
Source: https://osv.dev/vulnerability/CVE-2024-23452
Type: osv

## Details
Request smuggling vulnerability in HTTP server in Apache bRPC 0.9.5~1.7.0 on all platforms allows attacker to smuggle request.

Vulnerability Cause Description：

The http_parser does not comply with the RFC-7230 HTTP 1.1 specification.

Attack scenario:
If a message is received with both a Transfer-Encoding and a Content-Length header field, such a message might indicate an attempt to perform request smuggling or response splitting.
One particular attack scenario is that a bRPC made http server on the backend receiving requests in one persistent connection from frontend server that uses TE to parse request with the logic that 'chunk' is contained in the TE field. in that case an attacker can smuggle a request into the connection to the backend server. 

Solution:
You can choose one solution from below:
1. Upgrade bRPC to version 1.8.0, which fixes this issue. Download link:  https://github.com/apache/brpc/releases/tag/1.8.0
 2. Apply this patch:  https://github.com/apache/brpc/pull/2518

## References
- http://www.openwall.com/lists/oss-security/2024/02/08/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23452.json
- https://github.com/apache/brpc/releases/tag/1.8.0
- https://lists.apache.org/thread/kkvdpwyr2s2yt9qvvxfdzon012898vxd
- https://nvd.nist.gov/vuln/detail/CVE-2024-23452
- https://github.com/apache/brpc/pull/2518
