# [H] SwiftNIO: Out-of-bounds write via ByteBuffer index and length UInt32 overflow

## Summary
Severity: High
Advisory: GHSA-r3rc-9hpw-54v9
CVE: CVE-2026-43671
CWE: CWE-787
Ecosystem: SwiftURL
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-r3rc-9hpw-54v9
Type: github-advisory

## Affected
- SwiftURL: `github.com/apple/swift-nio` — affected >=1.0.0 <2.100.0

## Details
### Summary

A program using swift-nio is vulnerable to a potential out-of-bounds write when attacker-controlled index or length values exceeding `UInt32.max` are passed to some `ByteBuffer` methods. This affects all swift-nio versions from 1.0.0 to 2.99.0. It is fixed in 2.100.0 and later releases.

### Details

`ByteBuffer` internally stores indices and capacities as `UInt32` values. The internal helper functions `_toIndex` and `_toCapacity`, which convert from `Int` to `UInt32`, used `UInt32(truncatingIfNeeded:)`. On 64-bit platforms, this silently discards the upper 32 bits of the value rather than trapping on overflow. For example, a value of `UInt32.max + 1` (0x100000000) would be truncated to `0`.

This truncation can cause safety preconditions to pass when they should fail. Subsequent operations would then use the incorrect truncated value, potentially leading to out-of-bounds memory writes or reads.

The affected `ByteBuffer` methods that may lead to out-of-bounds writes are:

- `copyBytes(at:to:length:)` — a crafted destination index exceeding `UInt32.max` could copy bytes to an incorrect offset.
- `writeWithUnsafeMutableBytes(minimumWritableBytes:)` — a crafted `minimumWritableBytes` exceeding `UInt32.max` could provide the caller with a buffer pointer of incorrect length, which can easily be subsequently overflowed.

The affected `ByteBuffer` methods that have logic errors but do neither expose out-of-bounds reads nor out-of-bounds writes:

  - `moveReaderIndex(forwardBy:)` / `moveWriterIndex(forwardBy:)` — a crafted offset exceeding `UInt32.max` could move indices to incorrect positions, bypassing bounds checks. These indices cannot be out of the bounds of the buffer, so they do not expose access to uninitialized memory or produce wild pointers.
  - The `ByteBuffer(takingOwnershipOf:allocator:)` initialiser — passing a buffer larger than `UInt32.max` bytes could create a `ByteBuffer` with an incorrect capacity.

Outside of these methods, there are still impacts, but they are simply logical bugs. In these cases applications can be forced to read from or write to unexpected parts of the buffer. This does not cause memory-safety issues, but it can cause logical issues or corruption of outbound packets.

### Impact

Exploitation requires an attacker to influence the `index`, `offset`, or `length` parameter of the affected `ByteBuffer` methods with a value exceeding `UInt32.max` (approximately 4 GiB). This is a high bar for most applications: attacker-controlled length parameters to ByteBuffer are typically used on the read path, and the above methods are typically not used on the read paths. However, applications that calculate buffer positions arithmetically from untrusted input when attempting to do writes, or that process very large payloads, may be at risk of memory safety issues.

Other applications may encounter logical issues due to reading unexpected bytes, or writing to unexpected parts of the buffer.

When the memory-safety issue is exploitable, the consequences are severe. Because `truncatingIfNeeded` silently produces an incorrect but valid `UInt32` value, subsequent operations may write to or read from memory outside the valid buffer region. In optimised (release) builds where preconditions are not checked, this could lead to out-of-bounds memory writes, potentially corrupting adjacent heap memory.

In debug builds, some of these conditions are caught by assertions, but `truncatingIfNeeded` occurs before the assertion checks the (already-truncated) value, so even assertions may not reliably catch the issue.

### Patches

The issue is fixed by replacing `UInt32(truncatingIfNeeded:)` with `UInt32(_:)` in the `_toIndex` and `_toCapacity` helper functions. The `UInt32(_:)` initialiser traps on overflow in both debug and release builds, converting a potential silent memory corruption into a deterministic crash.

One call site in `getSlice(at:length:)` retains `truncatingIfNeeded` because prior bounds checks against the non-truncated `Int` values mathematically guarantee the values fit within `UInt32`.

### Workarounds

Applications can mitigate this issue by validating that all index and length values passed to `ByteBuffer` methods do not exceed `UInt32.max` (4,294,967,295). In practice, most applications are not affected because buffer indices are derived from protocol parsing rather than raw untrusted input.

## References
- https://github.com/apple/swift-nio/security/advisories/GHSA-r3rc-9hpw-54v9
- https://github.com/apple/swift-nio
