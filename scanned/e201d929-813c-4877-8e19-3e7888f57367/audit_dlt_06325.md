# [M] setWeight Allows Premature Weight Changes Through inadequate minimum time enforcement

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-25
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/34
Type: hats-finding

## Details
**Github username:** @ololade97
**Twitter username:** 97Sabit
**Submission hash (on-chain):** 0xc13f4d2009d58e303db426819e1d3cff28d9d721cb375b252bebab360ce28992
**Severity:** medium

**Description:**
**Description**\
Here's the comment in the setWeight function at line 148:

> 
// dev: targetTime must be more than MIN_ADJUSTMENT_TIME in the future.

MIN_ADJUSTMENT_TIME is 7 days between adjustments. setWeight() sets a new target weight for an asset. It requires targetTime >= block.timestamp + MIN_ADJUSTMENT_TIME.
Normally this enforces 7 days between weight changes.

However, since targetTime can be equal to the minimum:

A new target weight could be set every 7 days
Instead of waiting 7 days after the previous change.

For example:

- On Monday, weight is changed and targetTime is set to the following Monday.
- On next Monday, another adjustment is made, targetTime set to next Monday.
- Weights could change every Monday instead of every other Monday.

This doesn't ensure targetTime is more than MIN_ADJUSTMENT_TIME as specified in the comment.

**Attachments**
https://github.com/catalystdao/catalyst/blob/27b4d0a2bca177aff00def8cd745623bfbf7cb6b/evm/src/CatalystVaultVolatile.sol#L148

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

```

  require(targetTime >= block.timestamp + MIN_ADJUSTMENT_TIME); // dev: targetTime must be more than MIN_ADJUSTMENT_TIME in the future.

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/34_
