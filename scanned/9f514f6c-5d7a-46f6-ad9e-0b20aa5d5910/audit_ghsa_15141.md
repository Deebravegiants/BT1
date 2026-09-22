# [M] quic-go's path validation mechanism can be exploited to cause denial of service

## Summary
Severity: Medium
Advisory: GHSA-ppxx-5m9h-6vxf
CVE: CVE-2023-49295
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-01-10
Source: https://github.com/advisories/GHSA-ppxx-5m9h-6vxf
Type: github-advisory

## Affected
- Go: `github.com/quic-go/quic-go` — affected >=0.40.0 <0.40.1
- Go: `github.com/quic-go/quic-go` — affected >=0.39.0 <0.39.4
- Go: `github.com/quic-go/quic-go` — affected >=0.38.0 <0.38.2
- Go: `github.com/quic-go/quic-go` — affected >=0 <0.37.7

## Details
An attacker can cause its peer to run out of memory sending a large number of PATH_CHALLENGE frames. The receiver is supposed to respond to each PATH_CHALLENGE frame with a PATH_RESPONSE frame. The attacker can prevent the receiver from sending out (the vast majority of) these PATH_RESPONSE frames by collapsing the peers congestion window (by selectively acknowledging received packets) and by manipulating the peer's RTT estimate.

I published a more detailed description of the attack and its mitigation in this blog post: https://seemann.io/posts/2023-12-18-exploiting-quics-path-validation/

There's no way to mitigate this attack, please update quic-go to a version that contains the fix.

## References
- https://github.com/quic-go/quic-go/security/advisories/GHSA-ppxx-5m9h-6vxf
- https://nvd.nist.gov/vuln/detail/CVE-2023-49295
- https://github.com/quic-go/quic-go/commit/17fc98c2d81dbe685c19702dc694a9d606ac56dc
- https://github.com/quic-go/quic-go/commit/21609ddfeff93668c7625a85eb09f1541fdad965
- https://github.com/quic-go/quic-go/commit/3a9c18bcd27a01c551ac9bf8bd2b4bded77c189a
- https://github.com/quic-go/quic-go/commit/554d543b50b917369fb1394cc5396d928166cf49
- https://github.com/quic-go/quic-go/commit/6cc3d58935426191296171a6c0d1ee965e10534e
- https://github.com/quic-go/quic-go/commit/9aaefe19fc3dc8c8917cc87e6128bb56d9e9e6cc
- https://github.com/quic-go/quic-go/commit/a0ffa757499913f7be69aa78f573a6aee3430ae4
- https://github.com/quic-go/quic-go/commit/d7aa627ebde91cf799ada2a07443faa9b1e5abb8
- https://github.com/quic-go/quic-go
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/G5RSHDTVMYAIGYVVFGKTMFHAZJMA3EVV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZE7IOKXX5AATU2WR3V76X5Y3A44QAATG
- https://seemann.io/posts/2023-12-18-exploiting-quics-path-validation
