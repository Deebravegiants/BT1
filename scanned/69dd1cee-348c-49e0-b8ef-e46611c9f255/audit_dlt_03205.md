# [M] Slashing’s will Always Fail In Some Cases

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-07-karak
Published: 2024-07-24
Source: https://github.com/code-423n4/2024-07-karak-findings/issues/7
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-07-karak/blob/f5e52fdcb4c20c4318d532a9f08f7876e9afb321/src/Core.sol#L220
https://github.com/code-423n4/2024-07-karak/blob/f5e52fdcb4c20c4318d532a9f08f7876e9afb321/src/Vault.sol#L193
https://github.com/code-423n4/2024-07-karak/blob/f5e52fdcb4c20c4318d532a9f08f7876e9afb321/src/SlashingHandler.sol#L52


# Vulnerability details

## **Vulnerability Details:**

The [requestSlashing](https://github.com/code-423n4/2024-07-karak/blob/f5e52fdcb4c20c4318d532a9f08f7876e9afb321/src/Core.sol#L220) function allows a slashing to be requested for a given operator’s deployed vaults staked to the DSS.  The slashing request must pass the SLASHING_VETO_WINDOW (2 days) before it can be confirmed, allowing the veto committee to cancel any unfair queued slashing.

This time gap can create situations where the requested slashed amount is no longer possible, as the contract might have had previous withdrawals or been slashed by other DSS’s in that time, reducing its overall balance. The [slashAssets](https://github.com/code-423n4/2024-07-karak/blob/f5e52fdcb4c20c4318d532a9f08f7876e9afb321/src/Vault.sol#L193) function in the vault contract handles this by taking the minimum of the requested slashed amount and the contract balance.

```solidity
    function slashAssets(uint256 totalAssetsToSlash, address slashingHandler)
        external
        onlyCore
        returns (uint256 transferAmount)
    {
        transferAmount = Math.min(totalAssets(), totalAssetsToSlash);

        // Approve to the handler and then call the handler which will draw the funds
        SafeTransferLib.safeApproveWithRetry(asset(), slashingHandler, transferAmount);
        ISlashingHandler(slashingHandler).handleSlashing(IERC20(asset()), transferAmount);

        emit Slashed(transferAmount);
    }
```

However, if the total assets in the contract are zero, the transferAmount will be zero. When this zero value is passed to the [handleSlashing](https://github.com/code-423n4/2024-07-karak/blob/f5e52fdcb4c20c4318d532a9f08f7876e9afb321/src/SlashingHandler.sol#L52) function, it will revert due to a check that ensures the amount is not zero.

- Since DSS can slash 100% of a vault and vaults can be staked to multiple DSS, it is possible that a vault could be slashed before this slashing request, leaving its total assets as zero.
- Another scenario is if there were pending withdrawals that were completed before the slashing, resulting in the total assets being zero after the withdrawals.

```solidity

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-07-karak-findings/issues/7_
