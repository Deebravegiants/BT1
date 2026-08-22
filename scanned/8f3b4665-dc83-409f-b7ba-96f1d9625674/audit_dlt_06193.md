# [M] After a `TokenLock` is revoked tokens can be lost permanently

## Summary
Severity: Medium
Chain: Smart contract
Component: HATs-Arbitration-Contracts
Published: 2023-11-03
Source: https://github.com/hats-finance/HATs-Arbitration-Contracts-0x79a618f675857b45934ca1c413fd5f409cf89735/issues/54
Type: hats-finding

## Details
**Github username:** @bahurum
**Submission hash (on-chain):** 0x237585fadf9f48a0927a8dc394c515dc1870caa41a96c96dd44d586442969686
**Severity:** medium

**Description:**
**Description**\
In [`TokenLock.revoke()`](https://github.com/hats-finance/hats-contracts/blob/0d6ebbde912bc272d9b310140d434ee2aacd36d3/contracts/tokenlock/TokenLock.sol#L189) the unvested tokens are sent to the owner and the contract is destroyed afterwards.
The issue is that the unvested tokens are only a part of the total tokens inside the `TokenLock`, which is a sum of:
- unvested tokens
- vested tokens that have not been released by the `beneficiary` yet so are still in the contract. This amount is returned by `releasableAmount()`
- `surplusAmount()`

Since the contract is destroyed after it is revoked, `releasableAmount() + surplusAmount()` will be stuck permanently in the `TokenLock`.

**Recommendation**\
Consider returning `releasableAmount() + surplusAmount()` either to the owner or the beneficiary before the contract is destroyed.

To return to the owner:
```diff
function revoke() external override onlyOwner {
    if (!revocable)
        revert LockIsNonRevocable();

-   uint256 unvestedAmount = managedAmount - vestedAmount();
+   uint256 revokedAmount = token.balanceOf(address(this));
-   if (unvestedAmount == 0)
+   if (revokedAmount == 0)
        revert NoAvailableUnvestedAmount();

    isRevoked = true;

-   token.safeTransfer(owner(), unvestedAmount);
+   token.safeTransfer(owner(), revokedAmount);

-   emit TokensRevoked(beneficiary, unvestedAmount);
+   emit TokensRevoked(beneficiary, revokedAmount);

    selfdestruct(payable(msg.sender));
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/HATs-Arbitration-Contracts-0x79a618f675857b45934ca1c413fd5f409cf89735/issues/54_
