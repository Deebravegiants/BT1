# [H] td has pre-auth denial of service via unbounded memory allocation in proto.UnencryptedMessage.Decode

## Summary
Severity: High
Advisory: GHSA-whmm-qj9r-wvr2
CVE: CVE-2026-54638
CWE: CWE-770, CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-whmm-qj9r-wvr2
Type: github-advisory

## Affected
- Go: `github.com/gotd/td` — affected >=0 <0.145.1

## Details
### Impact

A remote, unauthenticated attacker can cause excessive memory allocation (and resulting CPU / GC pressure, potentially OOM termination) by sending a crafted unencrypted MTProto packet.

`(*proto.UnencryptedMessage).Decode` read an attacker-controlled 32-bit `dataLen` field and immediately allocated a buffer of that size via `make([]byte, dataLen)` **before** validating that the underlying buffer actually contained that many bytes. A 20-byte packet declaring a ~1.75 GB payload (e.g. `dataLen = 0x70000000`) forces the runtime to provision and zero-initialize a multi-gigabyte heap allocation before the length is rejected.

Unencrypted messages are part of the unauthenticated MTProto handshake path, so no credentials or established session are required to reach the vulnerable code.

Impact is limited to availability; there is no evidence of memory corruption, out-of-bounds access, or code execution.

### Patches

Fixed in **v0.145.1** by validating `dataLen` against the remaining buffer length before allocation (commit `9d5d1f31e`).

### Workarounds

Upgrade to v0.145.1 or later. There is no in-process workaround for affected versions short of avoiding exposure of the unauthenticated MTProto parsing path to untrusted peers.

## References
- https://github.com/gotd/td/security/advisories/GHSA-whmm-qj9r-wvr2
- https://github.com/gotd/td/issues/1711
- https://github.com/gotd/td/commit/9d5d1f31ea5022d9798d84ccce15de2e91ba6baa
- https://github.com/gotd/td
- https://github.com/gotd/td/releases/tag/v0.145.1
