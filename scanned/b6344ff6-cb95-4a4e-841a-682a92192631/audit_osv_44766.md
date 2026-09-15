# [M] Chainlit through 2.12.0 Path Traversal via socket.io sessionId

## Summary
Severity: Medium
Advisory: CVE-2026-86099
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86099
Type: osv

## Details
Chainlit through 2.12.0 fails to validate the client-supplied socket.io sessionId parameter, allowing unauthenticated attackers to traverse filesystem paths by injecting absolute or relative path sequences. Attackers can craft malicious sessionId values that escape the upload directory and recursively delete arbitrary directories accessible to the service process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86099.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86099
- https://www.vulncheck.com/advisories/chainlit-through-2.12.0-path-traversal-via-socket-io-sessionid
- https://github.com/Chainlit/chainlit
- https://pypi.org/project/chainlit/
- https://github.com/Chainlit/chainlit/blob/2.12.0/backend/chainlit/session.py
- https://github.com/Chainlit/chainlit/blob/2.12.0/backend/chainlit/socket.py
