# [M] In github.com/pion/webrtc, failed DTLS certificate verification doesn't stop data channel communication

## Summary
Severity: Medium
Advisory: GHSA-74xm-qj29-cq8p
CVE: CVE-2021-28681
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-05-25
Source: https://github.com/advisories/GHSA-74xm-qj29-cq8p
Type: github-advisory

## Affected
- Go: `github.com/pion/webrtc/v3` — affected >=0 <3.0.15

## Details
### Impact
Data channel communication was incorrectly allowed with users who have failed DTLS certificate verification.

This attack requires 
* Attacker knows the ICE password. 
* Only take place during PeerConnection handshake.

This attack can be detected by monitoring `PeerConnectionState` in all versions of Pion WebRTC.

### Patches
Users should upgrade to v3.0.15. 

The exact patch is https://github.com/pion/webrtc/commit/545613dcdeb5dedb01cce94175f40bcbe045df2e

### Workarounds
Users should listen for when `PeerConnectionState` changes to `PeerConnectionStateFailed`. When it enters this state users should not continue using the PeerConnection.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/pion/webrtc
* Email us at [team@pion.ly](mailto:team@pion.ly)

Thank you to https://github.com/Gaukas for discovering this.

## References
- https://github.com/pion/webrtc/security/advisories/GHSA-74xm-qj29-cq8p
- https://nvd.nist.gov/vuln/detail/CVE-2021-28681
- https://github.com/pion/webrtc/issues/1708
- https://github.com/pion/webrtc/pull/1709
- https://github.com/pion/webrtc/commit/545613dcdeb5dedb01cce94175f40bcbe045df2e
- https://github.com/pion/webrtc
- https://pkg.go.dev/vuln/GO-2021-0104
