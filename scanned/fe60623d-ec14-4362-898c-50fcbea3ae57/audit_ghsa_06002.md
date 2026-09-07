# [H] SIPSorcery vulnerable to Denial of Service via out-of-bounds read in SCTP SACK chunk parsing

## Summary
Severity: High
Advisory: GHSA-jwjp-4649-v8jp
CWE: CWE-125, CWE-755
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-12
Source: https://github.com/advisories/GHSA-jwjp-4649-v8jp
Type: github-advisory

## Affected
- NuGet: `SIPSorcery` — affected >=0 <10.0.14

## Details
## Summary
`SctpSackChunk.ParseChunk` reads the `numGapAckBlocks` and `numDuplicateTSNs` fields (each up to 65535) directly from an attacker-controlled SCTP SACK chunk and loops that many times reading 4 bytes per iteration, with no validation of the counts against the chunk length or the receive buffer. A single crafted SACK chunk from a negotiated WebRTC peer forces reads past the end of the 262144-byte receive buffer, raising `IndexOutOfRangeException`, which is not caught by the recoverable handler and terminates the dedicated SCTP receive thread — permanently killing the SCTP association and all data channels.

## Root Cause
`src/SIPSorcery/net/SCTP/Chunks/SctpSackChunk.cs`:
- `ushort numGapAckBlocks = NetConvert.ParseUInt16(buffer, startPosn + 8);` (:141)
- `ushort numDuplicateTSNs = NetConvert.ParseUInt16(buffer, startPosn + 10);` (:142)
- gap-ack loop (:146) and duplicate-TSN loop (:154) index the buffer via `NetConvert.ParseUInt16/32` (`buffer[posn]`, no bounds check — `sys/Net/NetConvert.cs:30,41`).
`SctpPacket.ParseChunks` (SctpPacket.cs:195-203) only validates `chunkLength >= 4` and `posn+chunkLength <= length`; the counts inside the value are never checked. `RTCSctpTransport.DoReceive` calls `SctpPacket.Parse(recvBuffer, 0, bytesRead)` on a reused `recvBuffer = new byte[262144]`.

## Impact
`IndexOutOfRangeException` is a `SystemException`, not `ApplicationException`, so the recoverable `catch (ApplicationException) { … continue; }` at RTCSctpTransport.cs:345 is skipped and control falls to the generic `catch (Exception) { … break; }` at :356. The `break` exits the receive loop, `DoReceive` returns, and the dedicated `_receiveThread = new Thread(DoReceive)` (:173, started once) exits with no restart → the SCTP association and every data channel are permanently dead (denial of service).

## Proof of Concept
A negotiated WebRTC peer (post-DTLS) sends a checksum-valid SCTP packet: 12-byte common header + a SACK chunk (type 3) with `chunkLength=16`, `numGapAckBlocks=0xFFFF`, `numDuplicateTSNs=0xFFFF`. CRC32C is attacker-computable. The gap-ack loop reaches `buffer[262144]` on a 262144-byte array (valid indices 0..262143) → `IndexOutOfRangeException`.

## Attack Chain
1. Entry: post-DTLS negotiated peer sends a checksum-valid SCTP packet with a SACK chunk (`chunkLength=16`, `numGapAckBlocks=0xFFFF`). Guard: `VerifyChecksum` (CRC32C). Bypass: CRC32C is computable by the sender.
2. Processing: `DoReceive` (RTCSctpTransport.cs:286) reads into reused `recvBuffer` (262144 bytes, :280) → `SctpPacket.Parse(recvBuffer, 0, bytesRead)` (:302) → `ParseChunks` → SACK dispatch (`SctpChunk.Parse` :340-341) → `SctpSackChunk.ParseChunk`. Guard: `ParseChunks` checks only `chunkLength>=4` and `posn+chunkLength<=length` (SctpPacket.cs:195-203). Bypass: `chunkLength=16` is well-formed; the counts are never validated.
3. Sink: gap-ack loop (SctpSackChunk.cs:146) calls `NetConvert.ParseUInt16(buffer, reportPosn)` with `reportPosn` starting at `startPosn(16)+FIXED_PARAMETERS(12)=28`, climbing `+4` each iteration. Guard: none on the count. Bypass: `NetConvert.ParseUInt16` (NetConvert.cs:30) indexes `buffer[posn]` unchecked.
4. Impact: at iteration 65529, `reportPosn = 28 + 65529*4 = 262144` → `buffer[262144]` → `IndexOutOfRangeException` → generic `catch` at RTCSctpTransport.cs:356 → `break` → receive thread exits, no restart → association permanently dead.

## Bypass Evidence
- Unchecked counts at SctpSackChunk.cs:141-142; loops at :146,:154.
- `NetConvert.ParseUInt16` unchecked indexing (NetConvert.cs:30).
- `ParseChunks` validates only `chunkLength` (SctpPacket.cs:195-203).
- OOB math: `28 + 65535*4 = 262168 > 262144`; buffer is 262144 (`DEFAULT_ADVERTISED_RECEIVE_WINDOW`, SctpAssociation.cs:62). `numGapAckBlocks` alone suffices — the dup-TSN loop is not needed.
- `DoReceive` catch split: recoverable `catch(ApplicationException)` at :345 (`continue`) vs generic `catch(Exception)` at :356 (`break`); `_receiveThread` started once at :176.

## Affected Versions
`nuget:SIPSorcery <= 10.0.13` (verified present on release tag v10.0.13 and HEAD da944543).

## Dedup
NOT a duplicate of GHSA-qmvg-569h-hqrh — that fix (`fe5a1fa`) touched only `SctpPacket.cs` (the chunk-cursor zero-length infinite loop, CWE-835). This is a distinct out-of-bounds read (CWE-125) in `SctpSackChunk` count loops, untouched by that fix.

## Suggested Fix
Validate `startPosn + FIXED_PARAMETERS_LENGTH + numGapAckBlocks*4 + numDuplicateTSNs*4 <= posn + chunkLen` before the loops, and/or make `NetConvert.Parse*` bounds-checked, and/or treat `IndexOutOfRangeException`/`ArgumentException` as recoverable in `DoReceive`.

---
Reported by **zx (Jace)** — GitHub: @manus-use

## References
- https://github.com/sipsorcery-org/sipsorcery/security/advisories/GHSA-jwjp-4649-v8jp
- https://github.com/sipsorcery-org/sipsorcery/commit/a2466550bb2a28821c73fb1961bc33dcc467f8cf
- https://github.com/sipsorcery-org/sipsorcery
