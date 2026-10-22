# [M] `totalUnderlyingMinusSponsored

## Summary
Severity: Medium
Contest weight: 0.5625
Dataset id: 1476
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function totalUnderlyingMinusSponsored() public view returns (uint256) {
        // TODO no invested amount yet
        return totalUnderlying() - totalSponsored;
    }
```

As a function that many other functions depended on, `totalUnderlyingMinusSponsored()` can revert on underflow when `sponsorAmount > totalUnderlying()` which is possible and has been considered elsewhere in this contract:

    if (_force && sponsorAmount > totalUnderlying()) {
        sponsorToTransfer = totalUnderlying();
    }

## Proof of Concept
* Underlying token = USDT
  * Swap Fee = 0.04%
  * Sponsor call `sponsor()` and send 10,000 USDT
  * totalSponsored = 10,000
  * `NonUSTStrategy.sol#doHardWork()` swapped USDT for UST
  * pendingDeposits = 9,996
  * totalUnderlying() = 9,996
  * Alice tries to call `deposit()`, the tx will revet due to underflow in `totalUnderlyingMinusSponsored()`.

## Recommendation
```solidity
function totalUnderlyingMinusSponsored() public view returns (uint256) {
        uint256 _totalUnderlying = totalUnderlying();
        if (totalSponsored > _totalUnderlying) {
            return 0;
        }
        return _totalUnderlying - totalSponsored;
    }
```
