# [M] arnika is affected by medium-severity issues in UDP rotation, PQC handling, and KMS TLS

## Summary
Severity: Medium
Advisory: GHSA-rc6v-5rmx-w5mv
CWE: CWE-294, CWE-295, CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:P/AC:L/PR:H/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-rc6v-5rmx-w5mv
Type: github-advisory

## Affected
- Go: `github.com/arnika-project/arnika` — affected >=0 <1.0.1

## Details
### Summary
Three medium-severity issues in arnika affecting the UDP key-rotation protocol, PQC key file handling, and KMS TLS client. All require specific preconditions to exploit and do not allow direct code execution or immediate key extraction. A self-contained PoC is attached.

### Details
1) ACK timestamp not validated: `udpserver.go:185`
`udpClient()` verifies HMAC and packet type but never checks `ackPkt.Timestamp`. A MITM can capture one ACK, drop all subsequent DATA packets, and replay the stale ACK indefinitely. Primary advances PSK each rotation, backup stays on key 1, tunnel breaks. No PSK knowledge needed. The server side already has this check, the client does not.
**Fix**: mirror the timestamp check already present on the server side.

2) Empty PQC key file silently accepted: `repositories/pqc.go:29`
`os.ReadFile` follows symlinks. Empty file to `base64.Decode("") = []byte{}, nil`. HKDF runs on the QKD key alone while arnika logs `[OK] HKDF derivation completed for QKD+PQC key`. Requires write access to the directory containing `PQC_PSK_FILE`.
**Fix**: validate decoded key is non-empty before derivation; enforce parent directory permissions in `SECURITY.md`.

3) `InsecureSkipVerify: true` hardcoded: `repositories/kms.go:61`
KMS HTTP client unconditionally sets `InsecureSkipVerify: true`, overriding `RootCAs`. `CA_CERTIFICATE` is loaded but never consulted (dead code). Requires MITM between arnika and the KMS endpoint, which in typical deployments are co-located.
**Fix**: remove the flag; `RootCAs` already holds the correct pool when `CA_CERTIFICATE` is configured.

### PoC
See [arnika_exploit.tar.gz](https://github.com/user-attachments/files/27585454/arnika_exploit.tar.gz). PoC shows observable behavior for each attack; the third one (KMS MITM) needs no custom code, any HTTPS proxy with a self-signed cert is enough.

### Impact
Issues require network MITM or local directory write access to exploit. No direct key extraction or code execution. Primary impact is tunnel desync and silent security downgrade in hybrid QKD+PQC mode.

## References
- https://github.com/arnika-project/arnika/security/advisories/GHSA-rc6v-5rmx-w5mv
- https://github.com/arnika-project/arnika/commit/efbd980d8b636cb59f60f2d6ece1b80a9cf36535
- https://github.com/arnika-project/arnika
- https://github.com/arnika-project/arnika/releases/tag/v1.0.1
