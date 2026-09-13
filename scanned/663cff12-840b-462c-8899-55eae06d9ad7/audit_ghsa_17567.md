# [H] quic-go Has Panic in Path Probe Loss Recovery Handling

## Summary
Severity: High
Advisory: GHSA-j972-j939-p2v3
CVE: CVE-2025-29785
CWE: CWE-248
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-06-03
Source: https://github.com/advisories/GHSA-j972-j939-p2v3
Type: github-advisory

## Affected
- Go: `github.com/quic-go/quic-go` — affected >=0.50.0 <0.50.1

## Details
### Impact

The loss recovery logic for path probe packets that was added in the v0.50.0 release can be used to trigger a nil-pointer dereference by a malicious QUIC client.

In order to do so, the attacker first sends valid QUIC packets from different remote addresses (thereby triggering the newly added path validation logic: the server sends path probe packets), and then sending ACKs for packets received from the server specifically crafted to trigger the nil-pointer dereference.

### Patches

v0.50.1 contains a patch that fixes the vulnerability.

This release contains a test that generates random sequences of sent packets (both regular and path probe packets), that was used to verify that the patch actually covers all corner cases.

### Workarounds

No.

### References

This issue has been reported publicly, but without any context, in https://github.com/quic-go/quic-go/issues/4981.

## References
- https://github.com/quic-go/quic-go/security/advisories/GHSA-j972-j939-p2v3
- https://nvd.nist.gov/vuln/detail/CVE-2025-29785
- https://github.com/quic-go/quic-go/issues/4981
- https://github.com/quic-go/quic-go/commit/b90058aba5f65f48e0e150c89bbaa21a72dda4de
- https://github.com/quic-go/quic-go
