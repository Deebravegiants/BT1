# [M] `enterExitQueue()` might be uncallable if the vault experiences a huge loss

## Summary
Severity: Medium
Chain: Smart contract
Component: StakeWise
Published: 2023-08-22
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/41
Type: hats-finding

## Details
**Github username:** @milotruck
**Submission hash (on-chain):** 0x811ea4ceb76e6ce6fb7e737e45c7488c327f4a4c16ccf0c9d5d5364b2e482d5a
**Severity:** medium

**Description:**
## Bug Description

In `VaultEnterExit.sol`, the `enterExitQueue()` is called by users to enter the exit queue. This adds their shares to `queuedShares`:

[VaultEnterExit.sol#L77-L80](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultEnterExit.sol#L77-L80)

```solidity
    unchecked {
      // cannot overflow as it is capped with _totalShares
      queuedShares = SafeCast.toUint96(_queuedShares + shares);
    }
```

Where:
- `shares` is the number of shares the caller wishes to withdraw. 

As seen from above, `shares` is downcast to a `uint96` since `queuedShares` has the type `uint96`.

This could potentially be a problem if the vault's shares to assets ratio is extremely high, as users will need to specify a large amount of shares to withdraw a substantial amount of assets. For example:

Assume the following:
- A vault currently has a 1 to 1 shares to assets ratio, which means that:
  - `totalShares = 32e18`
  - `totalAssets = 32 ether`
- The vault stakes its 32 ETH to register a validator.
- After a period of time, the validator is slashed with an extremely large penalty, causing it to lose most of its stake:
  - We assume that most of the validator's balance is slashed, leaving only `1e8` ETH remaining.
  - As a result, `totalAssets` is reduced to `1e8` for the vault.
- Now, if a user calls `deposit()` to deposit 1 ETH, he will get `32e28` shares:

```
shares = depositAmount * totalShares / totalAssets = 1e18 * 32e18 / 1e8 = 32e28
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/41_
