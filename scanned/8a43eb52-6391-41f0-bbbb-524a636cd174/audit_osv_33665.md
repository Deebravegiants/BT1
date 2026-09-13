# [M] Incorrect congestion window growth by optimistic ACK

## Summary
Severity: Medium
Advisory: CVE-2025-4820
Aliases: GHSA-2v9p-3p3h-w56j
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-4820
Type: osv

## Details
Impact

Cloudflare quiche was discovered to be vulnerable to incorrect congestion window growth, which could cause it to send data at a rate faster than the path might actually support.

An unauthenticated remote attacker can exploit the vulnerability by first completing a handshake and initiating a congestion-controlled data transfer towards itself. Then, it could manipulate the victim's congestion control state by sending ACK frames exercising an opportunistic ACK attack; see RFC 9000 Section 21.4. The victim could grow the congestion window beyond typical expectations and allow more bytes in flight than the path might really support.



Patches


quiche 0.24.4 is the earliest version containing the fix for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4820.json
- https://github.com/cloudflare/quiche/security/advisories/GHSA-2v9p-3p3h-w56j
- https://nvd.nist.gov/vuln/detail/CVE-2025-4820
