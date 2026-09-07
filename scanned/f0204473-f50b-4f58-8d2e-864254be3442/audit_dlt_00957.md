# [?] Merge bitcoin-core/HWI#825: Fix race condition in get_free_port (#802)

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin-core/HWI
Published: 2026-07-09
Source: https://github.com/bitcoin-core/HWI/commit/6847b4f5f571525fcb78775a39661b10a1d4d1e6
Type: security-commit

## Details
Merge bitcoin-core/HWI#825: Fix race condition in get_free_port (#802)

38f55ebd0551fa6e2957289d7df0b3987150ffe0 Fix race condition in get_free_port by binding to localhost (Rohit Yadav)

Pull request description:

  Fixes #802

  ### Problem
  The `get_free_port` function was previously binding to `""` (all interfaces). This caused a race condition where the OS would assign a port that appeared free on `0.0.0.0` but was actually unavailable or restricted when `bitcoind` specifically tried to bind to `127.0.0.1` milliseconds later.

  ### Solution
  I updated `s.bind(("", 0))` to `s.bind(("127.0.0.1", 0))`.
  This forces the OS to select a port specifically on the loopback interface ensuring it matches the interface `bitcoind` uses in the tests.

  ### Verification
  I verified locally that the function now returns a port explicitly bound to `127.0.0.1`.

ACKs for top commit:
  achow101:
    ACK 38f55ebd0551fa6e2957289d7df0b3987150ffe0

Tree-SHA512: 024d336bb2a79efe8b3fd358b265ea79a48d3798e7eadc063914712373d69906d0a96b84a2726cd686b8d57e2fa13ecc9513f3598d2cb916e68a1fec1661d9f0
