# [M] qcp has possible crash/DOS in some build configurations

## Summary
Severity: Medium
Advisory: GHSA-fmwf-c46w-r8qm
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-08
Source: https://github.com/advisories/GHSA-fmwf-c46w-r8qm
Type: github-advisory

## Affected
- crates.io: `qcp` — affected >=0 <0.3.3

## Details
**Nature of issue:** Crash (Denial of Service)
**Source of issue:** Dependent package (ring)
**Affected versions of qcp:** 0.1.0-0.3.2
**Recommendation:** Upgrade to qcp 0.3.3 or later

### Who is affected

All versions of qcp from 0.1.0 to 0.3.2 are affected, but **only if built with runtime overflow checks.**

* Released qcp binaries do not enable runtime overflow checks by default. **If you use an official released qcp binary download, you are not affected.**
* If you built qcp yourself in debug mode, you are affected unless your debug configuration explicitly disables overflow checks.
* If you built qcp yourself in release mode, you are only affected if you explicitly requested runtime overflow checks at build time by setting the appropriate `RUSTFLAGS`, or in your Cargo.toml profile.

### What to do if you are affected

**We recommend you upgrade to qcp 0.3.3 or later.**
Users upgrading from versions prior to 0.3.0 should note that an incompatible protocol change was introduced in version 0.3.0, so should stage their upgrade carefully.

Alternatively, it is possible to avoid upgrading by rebuilding qcp locally. The following alternative mitigations have been identified:
* Rebuild locally with runtime overflow checks disabled
* Rebuild locally using a fixed version of the `ring` dependency (0.17.12 or later).

### Detail

The upstream advisory describes a crash in the implementation of the QUIC protocol that can be induced by a specially-crafted packet, and which happens naturally approximately every 1 in 2**32 packets sent and/or received.

The crash only happens when runtime overflow checking is enabled. Note that the upstream advisory describes the overflow check causing this issue as "unwanted". Their response, to remove the overflow check in one place, does not introduce any additional issue.

### Impact

During qcp file transfer sessions, it is possible for an attacker to send a specially-crafted packet that could trigger this issue.
* In that case, and only if qcp was built with runtime overflow checks enabled, the effect is a Rust panic which immediately aborts the transfer. There is no additional impact on system resources at either end, nor on other file transfers in progress.
* As qcp runs a separate process for every connected user, the impact of the attack is limited to a single session.

The underlying issue may also affect particularly large file transfers. The maximum TLS packet size is 16KB, so 2**32 packets will transfer up to 68TB (including the protocol/retransmit overhead). Again, this is only the case if qcp was built with runtime overflow checks enabled.

As of the time of writing, we are not aware of any reports of this issue being exploited.

#### Additional notes
* The qcp protocol itself does not rely on runtime overflow checks for its security.
* While QUIC servers are normally public-facing, [qcp is a hybrid protocol](https://docs.rs/qcp/latest/qcp/protocol/index.html) that first requires an authenticated ssh session in order to set up the QUIC session. The window of attackability is therefore reduced, though will depend on your usage profile.
* An additional layer of obscurity is provided by qcp using ephemeral, random port numbers for its QUIC traffic (subject to user configuration).

### References
Upstream advisories:
* [RUSTSEC-2025-0009](https://rustsec.org/advisories/RUSTSEC-2025-0009.html)
* https://github.com/advisories/GHSA-4p46-pwfr-66x6

## References
- https://github.com/crazyscot/qcp/security/advisories/GHSA-fmwf-c46w-r8qm
- https://github.com/advisories/GHSA-4p46-pwfr-66x6
- https://github.com/briansmith/ring/blob/main/RELEASES.md#version-01712-2025-03-05
- https://github.com/crazyscot/qcp
- https://rustsec.org/advisories/RUSTSEC-2025-0009.html
