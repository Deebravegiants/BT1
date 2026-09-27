# [H] Incorrect congestion window growth by invalid ACK ranges

## Summary
Severity: High
Advisory: CVE-2025-4821
Aliases: GHSA-6m38-4r9r-5c4m
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-4821
Type: osv

## Details
Impact

Cloudflare quiche was discovered to be vulnerable to incorrect congestion window growth, which could cause it to send data at a rate faster than the path might actually support.

An unauthenticated remote attacker can exploit the vulnerability by first completing a handshake and initiating a congestion-controlled data transfer towards itself. Then, it could manipulate the victim's congestion control state by sending ACK frames covering a large range of packet numbers (including packet numbers that had never been sent); see RFC 9000 Section 19.3. The victim could grow the congestion window beyond typical expectations and allow more bytes in flight than the path might really support. In extreme cases, the window might grow beyond the limit of the internal variable's type, leading to an overflow panic.



Patches


quiche 0.24.4 is the earliest version containing the fix for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4821.json
- https://github.com/cloudflare/quiche/security/advisories/GHSA-6m38-4r9r-5c4m
- https://nvd.nist.gov/vuln/detail/CVE-2025-4821
