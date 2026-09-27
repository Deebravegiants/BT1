# [M] Resource exhaustion vulnerability in h2 may lead to Denial of Service (DoS)

## Summary
Severity: Medium
Advisory: GHSA-8r5v-vm4m-4g25
Ecosystem: crates.io
Published: 2024-01-19
Source: https://github.com/advisories/GHSA-8r5v-vm4m-4g25
Type: github-advisory

## Affected
- crates.io: `h2` — affected >=0 <0.3.24
- crates.io: `h2` — affected >=0.4.0 <0.4.2

## Details
An attacker with an HTTP/2 connection to an affected endpoint can send a steady stream of invalid frames to force the
generation of reset frames on the victim endpoint.
By closing their recv window, the attacker could then force these resets to be queued in an unbounded fashion,
resulting in Out Of Memory (OOM) and high CPU usage.

This fix is corrected in [hyperium/h2#737](https://github.com/hyperium/h2/pull/737), which limits the total number of
internal error resets emitted by default before the connection is closed.

## References
- https://github.com/hyperium/h2/pull/737
- https://github.com/hyperium/h2/commit/59570e11ccddbec85f67a0c7aa353f7730c68854
- https://github.com/hyperium/h2/commit/d919cd6fd8e0f4f5d1f6282fab0b38a1b4bf999c
- https://github.com/hyperium/h2
- https://rustsec.org/advisories/RUSTSEC-2024-0003.html
