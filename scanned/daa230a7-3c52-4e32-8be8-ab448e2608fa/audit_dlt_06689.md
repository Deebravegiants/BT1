# [H] a fake `dLoopCore` contract can steal leftover funds in `DLoopDepositorBase` because `DLoopDepositorBase::deposit()` does not restrict any `dLoopCore`input

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-27
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/279
Type: hats-finding

## Details
**Github username:** @CoheeYang
  **Twitter username:** @CoheeHimself
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/CoheeYang)

  **Beneficiary:** 0x9280209B3c436FEaA0e00A7eacEd4d75F7E4b2dC
  **Submission hash (on-chain):** 0x143b4e00bb1c58b3c7122e5dbd3f497e6c89dfcaa041f7b3e43b567565854a54
  **Severity:** high
  
  **Description:**
  ## **Description**

[DLoopDepositorBase::deposit()](https://github.com/dtrinity/sonic-solidity-contracts/blob/1844b73f78f0179228303d205271d510339e446b/contracts/vaults/dloop/periphery/DLoopDepositorBase.sol#L253-L353) does not restrict any `dLoopCore`address input,


```solidity
    function deposit(
        uint256 assets, // deposit amount
        address receiver,
        uint256 minOutputShares,
        bytes calldata debtTokenToCollateralSwapData,
        DLoopCoreBase dLoopCore
    ) public nonReentrant returns (uint256 shares) {
        ERC20 collateralToken = dLoopCore.collateralToken();
        ERC20 debtToken = dLoopCore.debtToken();

        // Transfer the collateral token to the vault (need the allowance before calling this function)
        // The remaining amount of collateral token will be flash loaned from the flash lender
        // to reach the leveraged amount
        collateralToken.safeTransferFrom(msg.sender, address(this), assets);

        // Calculate the estimated overall slippage bps
        uint256 estimatedOverallSlippageBps = _calculateEstimatedOverallSlippageBps(
                dLoopCore.convertToShares(dLoopCore.getLeveragedAssets(assets)),
                minOutputShares
            );

        // Make sure the estimated overall slippage bps does not exceed 100%
        if (
            estimatedOverallSlippageBps >
            BasisPointConstants.ONE_HUNDRED_PERCENT_BPS
        ) {
            revert EstimatedOverallSlippageBpsCannotExceedOneHundredPercent(
                estimatedOverallSlippageBps
            );
        }

        // Calculate the leveraged collateral amount to deposit with slippage included
        // Explained with formula in _calculateEstimatedOverallSlippageBps()
        uint256 leveragedCollateralAmount = (dLoopCore.getLeveragedAssets(
            assets
        ) *
            (BasisPointConstants.ONE_HUNDRED_PERCENT_BPS -
                estimatedOverallSlippageBps)) /
            BasisPointConstants.ONE_HUNDRED_PERCENT_BPS;

        // Create the flash loan params data
        FlashLoanParams memory params = FlashLoanParams(
            receiver,
            assets,
            leveragedCollateralAmount,
            debtTokenToCollateralSwapData,
            dLoopCore
        );
        bytes memory data = _encodeParamsToData(params);
        uint256 maxFlashLoanAmount = flashLender.maxFlashLoan(
            address(debtToken)
        );

        // This value is used to check if the shares increased after the flash loan
        uint256 sharesBeforeDeposit = dLoopCore.balanceOf(address(this));

        // Approve the flash lender to spend the flash loan amount of debt token from this contract
        ERC20(debtToken).forceApprove(
            address(flashLender),
            maxFlashLoanAmount +
                flashLender.flashFee(address(debtToken), maxFlashLoanAmount)
        );

        // Make sure the flashLender is the same as the debt token
        if (address(flashLender) != address(debtToken)) {
            revert FlashLenderNotSameAsDebtToken(
                address(flashLender),
                address(debtToken)
            );
        }

        // The main logic will be done in the onFlashLoan function
        flashLender.flashLoan(
            this,
            address(debtToken),
            maxFlashLoanAmount,
            data
        );

        // The received debt token after deposit was used to repay the flash loan

        // Check if the shares increased after the flash loan
        uint256 sharesAfterDeposit = dLoopCore.balanceOf(address(this));
        if (sharesAfterDeposit <= sharesBeforeDeposit) {
            revert SharesNotIncreasedAfterFlashLoan(
                sharesBeforeDeposit,
                sharesAfterDeposit
            );
        }

        // Finalize deposit and transfer shares
        return
            _finalizeDepositAndTransfer(
                dLoopCore,
                debtToken,
                receiver,
                sharesBeforeDeposit,
                sharesAfterDeposit,
                minOutputShares
            );
    }
```

And in `_finalizeDepositAndTransfer()`,this function will pass the input address`dLoopCore` to call  `_handleLeftoverDebtTokens`, and transfer all the debtToken in this contract if `leftoverAmount`  is greater than `minLeftoverDebtTokenAmount[address(dLoopCore)][address(debtToken)]`


```solidity
    function _handleLeftoverDebtTokens(
        DLoopCoreBase dLoopCore,
        ERC20 debtToken
    ) internal {
        uint256 leftoverAmount = debtToken.balanceOf(address(this));
        if (
            leftoverAmount >
            minLeftoverDebtTokenAmount[address(dLoopCore)][address(debtToken)]
        ) {
            // Transfer any leftover debt tokens to the core contract
            debtToken.safeTransfer(address(dLoopCore), leftoverAmount);
            emit LeftoverDebtTokensTransferred(
                address(dLoopCore),
                address(debtToken),
                leftoverAmount
            );
        }
    }

```
The missing input restriction allows an attacker to create a fake `DLoopCoreBase `  contract to call `deposit`, and then sweep the leftover tokens that remains in the `DLoopDepositorBase`






# **Proof of Concept (PoC)**
1. after deployment, the owner calls `DLoopDepositorBase::setMinLeftoverDebtTokenAmount()` to set a threshold for a target `dLoopCore`.

2. some users calls `DLoopDepositorBase::deposit()`,but the leftover debt token amount does not exceeds the threshold, so the debt token remains in the contract.
3.  A melicisou attacker creates a fake `dLoopCore` whose `debtToken()` and `collateralToken` are identical to the victim `dLoopCore`.
4. the attacker send some `debtToken` to this fake `dLoopCore`so that this contract can send back `debtToken` when `DLoopDepositorBase` calls its deposit function during the flashLoan
5.  the attacker calls `DLoopDepositorBase::deposit()`, sending some collateral tokens to `DLoopDepositorBase`, and these collateral token and debtTokens sent by attacker in step 4 will go to the fake contract in a form of collateral token.
6.  The remaining debtToken in step 2 is also transfered to the fake contract
7.  attacker withdraw all the tokens from the fake contracts, and successfully steal the leftover tokens

# **Migration**
add a check before the leverage deposit to prevent any stealing of funds.


```solidity
function deposit(
        uint256 assets, // deposit amount
        address receiver,
        uint256 minOutputShares,
        bytes calldata debtTokenToCollateralSwapData,
        DLoopCoreBase dLoopCore
    ) public nonReentrant returns (uint256 shares) {
+      require(allowed[dLoopCore]);
        ERC20 collateralToken = dLoopCore.collateralToken();
        ERC20 debtToken = dLoopCore.debtToken();
...

```
