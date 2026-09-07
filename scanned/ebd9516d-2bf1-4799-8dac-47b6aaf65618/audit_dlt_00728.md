# [?] hardening: Add range checks to prevent signed integer overflow UB.

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2026-04-10
Source: https://github.com/zcash/zcash/commit/de16cd0a0c7cc7f9be8ce164d17ca970b20c0feb
Type: security-commit

## Details
hardening: Add range checks to prevent signed integer overflow UB.

Add range checks for integer arithmetic on CAmount values to prevent
signed integer overflow (undefined behavior in C++).

In SetChainPoolValues: check each running sum of per-pool deltas
(saplingValue, orchardValue, sproutValue) after every mutation,
ensuring it stays within [-MAX_MONEY, MAX_MONEY]. Make the function
return bool so callers can reject blocks with out-of-range deltas.

In ReceivedBlockTransactions: check parent chain values are in
MoneyRange and per-block deltas are in MoneyDeltaRange before each
addition.

In ConnectBlock: check chainSupplyDelta, transparentValueDelta,
cbTotalOutputValue, cbTotalInputValue, txFee, and nFees after each
mutation. Check parent nChainTotalSupply and nChainTransparentValue
are in MoneyRange before and after accumulating.

In LoadBlockIndexDB: add the same pre- and post-addition checks for
all six pool value accumulations and the total supply / transparent
value accumulations. On-disk per-block deltas could be corrupted by
a prior vulnerable version, so we cannot assume they are in range.

In GetTransparentValueIn and GetValueIn: add MoneyRange checks on
the running sum, matching the existing checks in GetValueOut and
GetShieldedValueIn. GetTransparentValueIn can sum up to ~48K inputs
per block (MAX_BLOCK_SIZE / ~41 bytes per input), which at MAX_MONEY
each would exceed INT64_MAX. The intermediate overflow cannot be
prevented at call sites, only inside the loop. Throwing is consistent
with GetValueOut and GetShieldedValueIn, which already throw on range
violations, so callers already need to handle exceptions from value
computation.

Add a MoneyDeltaRange helper ([-MAX_MONEY, MAX_MONEY]) alongside the
existing MoneyRange ([0, MAX_MONEY]) for checking per-block deltas
that may be negative. Use it in GetValueOut for consistency.


_Trimmed to 38 lines — full report: https://github.com/zcash/zcash/commit/de16cd0a0c7cc7f9be8ce164d17ca970b20c0feb_
