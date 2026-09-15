# [M] webtransport-go: CloseWithError can block indefinitely

## Summary
Severity: Medium
Advisory: GHSA-px4r-g4p3-hhqv
CVE: CVE-2026-21435
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-12
Source: https://github.com/advisories/GHSA-px4r-g4p3-hhqv
Type: github-advisory

## Affected
- Go: `github.com/quic-go/webtransport-go` — affected >=0 <0.10.0

## Details
## Summary
An attacker can cause a denial of service in webtransport-go by preventing or indefinitely delaying WebTransport session closure. A malicious peer can withhold QUIC flow control credit on the CONNECT stream, blocking transmission of the WT_CLOSE_SESSION capsule and causing the close operation to hang.

## Details
WebTransport over HTTP/3 signals session termination by sending a WT_CLOSE_SESSION capsule on the CONNECT stream. The capsule is only needed to transmit a reason phrase and an error code to the peer. After the capsule is sent, the CONNECT stream is closed.
In affected versions, the closure procedure blocked indefinitely while waiting for sufficient QUIC flow control credit from the peer. A malicious peer can withhold this credit, preventing the capsule from being sent.

## The Fix
webtransport-go now attempts to send the WT_CLOSE_SESSION capsule with a short deadline. If the capsule cannot be sent within this deadline, the CONNECT stream is reset instead. This closes the WebTransport session promptly without transmitting the optional error details.
This prevents indefinite blocking on session closure.

## References
- https://github.com/quic-go/webtransport-go/security/advisories/GHSA-px4r-g4p3-hhqv
- https://nvd.nist.gov/vuln/detail/CVE-2026-21435
- https://github.com/quic-go/webtransport-go
- https://github.com/quic-go/webtransport-go/releases/tag/v0.10.0
