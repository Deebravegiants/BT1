# [M] `MultiStrategy#removeStrategy`

## Summary
Severity: Medium
Contest weight: 0.6273
Dataset id: 22297
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the MultiStrategyVault’s removeStrategy function, which assumes that calling a strategy’s undeploy method will always return the exact amount of assets that were previously deployed. This assumption holds for simple strategies but breaks for leverage strategies that rely on flash‑loan‑driven debt repayment and collateral swaps. When a leveraged strategy is removed, the undeploy routine borrows debt, repays it to unlock collateral, swaps the collateral back to the debt token and finally repays the flash loan plus fee. Because the swap may incur slippage, fees, or unfavorable price oracle data, the net amount of debt token that can be reclaimed is often lower than the original deployed amount. The removeStrategy code does not verify that the amount received from _undeploy matches the expected strategyAssets; it simply forwards the possibly reduced amount to _allocateAssets and proceeds to delete the strategy entry. Consequently, the vault’s accounting becomes inconsistent: the total weight is reduced, but the actual assets that remain in the vault are smaller than anticipated. From a user’s perspective this manifests as a missing or reduced balance after a strategy is removed – a user expects their funds to be re‑allocated or refunded in full, yet sees a lower amount or even zero. The issue is triggered only when the removed strategy is a leverage strategy with non‑zero deployed assets, and it is exploitable by any entity with the VAULT_MANAGER_ROLE who can deliberately remove such a strategy, causing a shortfall that may be difficult to recover. The problem was discovered during a Code4rena audit when the auditors compared the expected asset flow with the actual return from a leveraged strategy’s undeploy call and noticed a discrepancy. The bug is subtle because the function signatures and event logs appear normal, and the shortfall is hidden inside the flash‑loan logic rather than being an explicit revert. To remediate, the contract should either enforce that the undeploy returns at least the requested amount (reverting otherwise), adjust the weight and total asset accounting to reflect any shortfall, or redesign the removal process to handle leveraged strategies separately, ensuring that users’ balances remain consistent with protocol accounting rules.

## Proof of Concept
`MultiStrategyVault` is used to manage multiple investment strategies. The vault manager can remove an existing strategy by calling `MultiStrategy#removeStrategy()`:

```solidity
function removeStrategy(uint256 index) external onlyRole(VAULT_MANAGER_ROLE) {
    // Validate the index to ensure it is within bounds
    if (index >= _strategies.length) revert InvalidStrategyIndex(index);

    // Retrieve the total assets managed by the strategy to be removed
    uint256 strategyAssets = _strategies[index].totalAssets();

    // Update the total weight and mark the weight of the removed strategy as zero
    _totalWeight -= _weights[index];
    _weights[index] = 0;

    // If the strategy has assets, undeploy them and allocate accordingly
    if (strategyAssets > 0) {
        IStrategy(_strategies[index]).undeploy(strategyAssets);
        _allocateAssets(strategyAssets);
    }

    // Move the last strategy to the index of the removed strategy to maintain array integrity
    uint256 lastIndex = _strategies.length - 1;
    if (index < lastIndex) {
        _strategies[index] = _strategies[lastIndex];
        _weights[index] = _weights[lastIndex];
    }

    emit RemoveStrategy(address(_strategies[lastIndex]));
    // Remove the last strategy and weight from the arrays
    _strategies.pop();
    _weights.pop();
}
```

If the strategy to be removed has deployed assets, it will be undeployed first and then allocated to other strategies. It is expected that the equivalent amount of assets will be received when calling `IStrategy.undeploy()`:

```solidity
IStrategy(_strategies[index]).undeploy(strategyAssets);
_allocateAssets(strategyAssets);
```

However, the amount of received assets could be less than `strategyAssets` if the strategy is a leverage strategy.

When a leverage strategy is used to undeploy assets:

  1. `deltaDebt` of debt token will be borrowed from `flashLender`
  2. Then the borrowed debt token is repaid to the lending protocol to withdraw `deltaCollateralAmount` of collateral
  3. The withdrawn collateral is swapped to debt token
  4. A certain number (`deltaDebt + fee`) of debt token will be paid to `flashLender`

```solidity
function _undeploy(uint256 amount, address receiver) private returns (uint256 receivedAmount) {
    // Get price options from settings
    IOracle.PriceOptions memory options = IOracle.PriceOptions({
        maxAge: getPriceMaxAge(),
        maxConf: getPriceMaxConf()
    });

    // Fetch collateral and debt balances
    (uint256 totalCollateralBalance, uint256 totalDebtBalance) = getBalances();
    uint256 totalCollateralInDebt = _toDebt(options, totalCollateralBalance, false);

    // Ensure the position is not in liquidation state
    if (totalCollateralInDebt <= totalDebtBalance) revert NoCollateralMarginToScale();

    // Calculate percentage to burn to accommodate the withdrawal
    uint256 percentageToBurn = (amount * PERCENTAGE_PRECISION) / (totalCollateralInDebt - totalDebtBalance);

    // Calculate delta position (collateral and debt)
    (uint256 deltaCollateralInDebt, uint256 deltaDebt) = _calcDeltaPosition(
        percentageToBurn,
        totalCollateralInDebt,
        totalDebtBalance
    );
    // Convert deltaCollateralInDebt to deltaCollateralAmount
    uint256 deltaCollateralAmount = _toCollateral(options, deltaCollateralInDebt, true);

    // Calculate flash loan fee
    uint256 fee = flashLender().flashFee(_debtToken, deltaDebt);

    // Approve the flash lender to spend the debt amount plus fee
    if (!IERC20Upgradeable(_debtToken).approve(flashLenderA(), deltaDebt + fee)) {
        revert FailedToApproveAllowance();
    }

    // Prepare data for flash loan execution
    bytes memory data = abi.encode(deltaCollateralAmount, receiver, FlashLoanAction.PAY_DEBT_WITHDRAW);
    _flashLoanArgsHash = keccak256(abi.encodePacked(address(this), _debtToken, deltaDebt, data));

    // Execute flash loan
    if (!flashLender().flashLoan(IERC3156FlashBorrowerUpgradeable(this), _debtToken, deltaDebt, data)) {
        _flashLoanArgsHash = 0;
        revert FailedToRunFlashLoan();
    }
    // The amount of Withdrawn minus the repay ampunt
    emit StrategyUndeploy(msg.sender, deltaCollateralInDebt - deltaDebt);

    // Reset hash after successful flash loan
    _flashLoanArgsHash = 0;

    // Update deployed assets after withdrawal
    receivedAmount = _pendingAmount;
    uint256 undeployedAmount = deltaCollateralInDebt - deltaDebt;
    _deployedAssets = _deployedAssets > undeployedAmount ? _deployedAssets - undeployedAmount : 0;

    // Emit strategy update and reset pending amount
    emit StrategyAmountUpdate(_deployedAssets);
    // Pending amount is not cleared to save gas
    //_pendingAmount = 0;
}
```

The amount of received assets can be calculated as below:

Note: please see scenario in warden’s[original submission](https://code4rena.com/evaluate/2024-12-bakerfi-invitational/findings/F-5).

## Recommendation
No recommendation
