# [M] CVE-2024-48075

## Summary
Severity: Medium
Advisory: CVE-2024-48075
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-11-12
Source: https://osv.dev/vulnerability/CVE-2024-48075
Type: osv

## Details
A Heap buffer overflow in the server-site handshake implementation in Real Time Logic SharkSSL from 09/09/24 and earlier allows a remote attacker to trigger a Denial-of-Service via a malformed TLS Client Key Exchange message.

## References
- https://www.telekom.com/resource/blob/1083076/8bf5c03520005b8e699dfb9bce470fc7/dl-241104-cve-2024-48075-data.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48075.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48075
- https://github.com/RealTimeLogic/SharkSSL/commit/7045f6f254060640ff77eef2027f108fcc20e2f2
