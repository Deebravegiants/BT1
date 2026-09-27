# [H] QUIC's Connection ID Mechanism vulnerable to Memory Exhaustion Attack

## Summary
Severity: High
Advisory: GHSA-c33x-xqrf-c478
CVE: CVE-2024-22189
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-02
Source: https://github.com/advisories/GHSA-c33x-xqrf-c478
Type: github-advisory

## Affected
- Go: `github.com/quic-go/quic-go` — affected >=0 <0.42.0

## Details
An attacker can cause its peer to run out of memory by sending a large number of NEW_CONNECTION_ID frames that retire old connection IDs. The receiver is supposed to respond to each retirement frame with a RETIRE_CONNECTION_ID frame. The attacker can prevent the receiver from sending out (the vast majority of) these RETIRE_CONNECTION_ID frames by collapsing the peers congestion window (by selectively acknowledging received packets) and by manipulating the peer's RTT estimate.

I published a more detailed description of the attack and its mitigation in this blog post: https://seemann.io/posts/2024-03-19-exploiting-quics-connection-id-management/.
I also presented this attack in the IETF QUIC working group session at IETF 119: https://youtu.be/JqXtYcZAtIA?si=nJ31QKLBSTRXY35U&t=3683

There's no way to mitigate this attack, please update quic-go to a version that contains the fix.

## References
- https://github.com/quic-go/quic-go/security/advisories/GHSA-c33x-xqrf-c478
- https://nvd.nist.gov/vuln/detail/CVE-2024-22189
- https://github.com/quic-go/quic-go/commit/4a99b816ae3ab03ae5449d15aac45147c85ed47a
- https://github.com/quic-go/quic-go
- https://seemann.io/posts/2024-03-19-exploiting-quics-connection-id-management
- https://www.youtube.com/watch?v=JqXtYcZAtIA&t=3683s
