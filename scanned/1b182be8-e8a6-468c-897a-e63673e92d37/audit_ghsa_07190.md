# [M] jxl-oxide: `FrameBuffer::new` creates out-of-bounds slices on overflow

## Summary
Severity: Medium
Advisory: GHSA-66m8-c62j-h6v5
CWE: CWE-131, CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-66m8-c62j-h6v5
Type: github-advisory

## Affected
- crates.io: `jxl-oxide` — affected >=0 <0.12.6

## Details
### Summary
`jxl-oxide` exposes a public safe API that can construct an undersized `FrameBuffer` due to unchecked `usize` multiplication, which immediately trigger panic while initializing the buffer in normal decoding path.

Additionally, calling the safe grouped buffer accessors afterward can create invalid oversized slices from a much smaller allocation, causing undefined behavior; however normal decoding path never reaches UB, because these methods are never used within `jxl-oxide`.

### Impact
On 32-bit platforms this can cause panic by accessing out-of-range indices, making it a DoS vulnerability.

## References
- https://github.com/tirr-c/jxl-oxide/security/advisories/GHSA-66m8-c62j-h6v5
- https://github.com/tirr-c/jxl-oxide
