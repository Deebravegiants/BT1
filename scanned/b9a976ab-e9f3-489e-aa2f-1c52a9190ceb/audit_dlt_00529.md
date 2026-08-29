# [?] execution, cl, common/math: fix unchecked integer overflows on untrusted input (#23192)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-08-13
Source: https://github.com/erigontech/erigon/commit/3a8f182db1799ca1b9c1f5702fdba51e4dd0e678
Type: security-commit

## Details
execution, cl, common/math: fix unchecked integer overflows on untrusted input (#23192)

Two unchecked integer overflows in code that parses untrusted input,
found by compiling the unit suite with
[gosentry](https://github.com/trailofbits/gosentry)'s arithmetic
instrumentation (`go test -short ./...` surfaced 116 panics across 18
sites; the rest were intentional wraparound in SWAR, hashing and crypto
code).

**RIP-7560 gas limits sum without an overflow check.**
`ValidationGasLimit`, `PaymasterValidationGasLimit`, `GasLimit` and
`PostOpGasLimit` come off the wire unvalidated and were added in four
places. `chargeGas` turns the wrapped total into `preCharge` and
compares it against the payer's balance, so a wrapped-small total passes
the insufficient-funds check; `refundGas` then computes `preCharge -
actualGasCost` from the same value.

**A bitlist with no sentinel bit corrupts its hash tree root.**
`parseBitlist` reads `bits.Len8(last) - 1`; when the last byte is zero
that underflows to 255 and inflates the length mixed into the root. An
empty buffer indexed out of range.

| case | main | this PR |
| --- | --- | --- |
| `GetGasLimit()` with `ValidationGasLimit = MaxUint64` | `15000` (base
cost alone) | `MaxUint64`, checks fail closed |
| `chargeGas` / `refundGas` on an overflowing sum | wrapped total used |
rejected with `ErrGasLimitReached` |
| `BitlistRootWithLimit([]byte{0x00})` | length 255 mixed into root |
length 0 |
| `BitlistRootWithLimit([]byte{})` | `index out of range [-1]` | length
0 |

Both regression tests were confirmed to fail on unfixed code before the
fix landed.

**`SafeSub` restored.** geth's `common/math` carries `SafeAdd`,
`SafeSub` and `SafeMul`; erigon's copy dropped `SafeSub`, even though

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/3a8f182db1799ca1b9c1f5702fdba51e4dd0e678_
