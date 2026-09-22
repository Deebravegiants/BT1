# [H] Unbounded path event queue growth in quiche via peer-driven source connection ID rotation

## Summary
Severity: High
Advisory: CVE-2026-12707
Aliases: GHSA-4q5x-gp38-rfp4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-12707
Type: osv

## Details
Summary



Cloudflare quiche was discovered to be vulnerable to memory resource exhaustion due to unbounded queuing of post-handshake client migration events.



Impact



quiche supports the connection migration features described in Section 9 of RFC 9000, which allows a single QUIC connection to survive changes in the network path. Although quiche implements the protections described in Section 9.3 of RFC 9000 to limit server state commitment, it was discovered that the collection of PathEvents, intended to be consumed by applications via the path_event_next() function, was not bounded.



Once the QUIC handshake completed, a peer could exploit rapid source address migration in order to cause unbounded queuing of the PathEvent::ReusedSourceConnectionId type. Servers are vulnerable even if active connection migration is disabled.



Mitigation:

  *  

Applications can call path_event_next() to drain the PathEvent collection, mitigating the attack.


  *  

Users are requested to upgrade to quiche 0.29.3 which is the earliest version that prevents excessive queueing of PathEvent::ReusedSourceConnectionId.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12707.json
- https://github.com/cloudflare/quiche/security/advisories/GHSA-4q5x-gp38-rfp4
- https://nvd.nist.gov/vuln/detail/CVE-2026-12707
- https://github.com/cloudflare/quiche
