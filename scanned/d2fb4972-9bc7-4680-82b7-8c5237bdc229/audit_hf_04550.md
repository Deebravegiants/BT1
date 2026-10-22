# [H] `CDPVault.sol#liquidatePositionBadDebt`

## Summary
Severity: High
Contest weight: 0.7438
Dataset id: 22134
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the liquidation routine of the CDPVault contract, specifically the function that handles bad‑debt positions. When a borrower’s collateral is insufficient to cover the total debt (principal plus accrued interest), the contract calculates a loss as the difference between the total debt and the amount that can be repaid from the collateral. However, the profit value is derived only from the excess of the repayment over the principal, ignoring the accrued interest that should be treated as profit. The function then forwards the principal, the computed profit, and the loss to the PoolV3 contract via pool.repayCreditAccount. Because profit is set to zero in many bad‑debt scenarios, the PoolV3 logic mints treasury shares only when profit > 0 and burns shares when loss > 0. The incorrect profit calculation causes the pool to burn far more treasury shares than the actual shortfall, while minting too few (or none) when interest should be credited. This mis‑accounting leads to an imbalance in the treasury’s share balance, effectively reducing the value of LP‑ETH tokens held by stakers and causing funds to disappear from the pool’s accounting. The flaw manifests during any liquidation where the collateral value, after applying the discount price, is lower than the total debt, a condition that can be triggered by market price drops or deliberately crafted positions. It primarily affects liquidity providers, the protocol’s overall solvency, and any user expecting accurate redemption values. The issue was uncovered during a formal audit when the auditors compared the expected accounting outcome with the actual state changes and identified that the loss handling burned excessive shares. The problem is subtle because the treasury share balance may not change dramatically in a single liquidation, making the discrepancy hard to spot until many such events accumulate. To remediate, the liquidation code should pass the accrued interest as the profit argument (i.e., use debtData.accruedInterest instead of zero) and ensure that loss reflects only the principal shortfall, thereby aligning the minting and burning of treasury shares with the true economic outcome of the liquidation.

## Recommendation
In CDPVault, change to `pool.repayCreditAccount(debtData.debt, debtData.accruedInterest, loss)`.

In PoolV3:
    
```solidity
if (profit > 0) {
    _mint(treasury, convertToShares(profit)); // U:[LP-14B]
}
if (loss > 0)
else if (loss > 0) {
    ...
}
```

Why Profit should be `debtData.accruedInterest`?

For the second part, could you please provide a case where profit and loss are non-zero in PJQA?

@Koolex - Here’s an example scenario:

  1. User originally taken out a debt of 100, and interest grows to 50, so `debtData.debt = 100, debtData.accruedInterest = 50, calcTotalDebt(debtData) = 150)`.
  2. User collateral is only 100, and after multiplying `discountPrice`, the `repayAmount` is only 90. Bad debt occurs.
  3. `loss = calcTotalDebt(debtData) - repayAmount` is equal to `150 - 90 = 60`.
  4. Since `repayAmount < debtData.debt`, we would have `profit = 0`.

This means for `PoolV3#repayCreditAccount`, 60 shares would be burned from the treasury, while instead it should be 10 (because original debt was 100, repaid is 90, `100 - 90 = 10`).

You can also see that if `repayAmount` was 101, we would calculate `profit = 1`, and in `PoolV3#repayCreditAccount` we would mint 1 share instead. This means there is a 61 (`1 - (-60) = 61`) gap in treasury shares when the repaid amount diff is only 11 (`101 - 90 = 11`), which does not make any sense.
     
     
```solidity
function calcTotalDebt(DebtData memory debtData) internal pure returns (uint256) {
    return debtData.debt + debtData.accruedInterest; //+ debtData.accruedFees;
}

function liquidatePositionBadDebt(address owner, uint256 repayAmount) external whenNotPaused {
    ...
    takeCollateral = position.collateral;
    repayAmount = wmul(takeCollateral, discountedPrice);
    uint256 loss = calcTotalDebt(debtData) - repayAmount;
    uint256 profit;
    if (repayAmount > debtData.debt) {
        profit = repayAmount - debtData.debt;
    }
    ...
    pool.repayCreditAccount(debtData.debt, profit, loss); // U:[CM-11]
    // transfer the collateral amount from the vault to the liquidator
    token.safeTransfer(msg.sender, takeCollateral);
}
```

PoolV3.sol:
     
```solidity
function repayCreditAccount(
    uint256 repaidAmount,
    uint256 profit,
    uint256 loss
)
    external
    override
    creditManagerOnly // U:[LP-2C]
    whenNotPaused // U:[LP-2A]
    nonReentrant // U:[LP-2B]
{
    uint128 repaidAmountU128 = repaidAmount.toUint128();

    DebtParams storage cmDebt = _creditManagerDebt[msg.sender];
    uint128 cmBorrowed = cmDebt.borrowed;
    if (cmBorrowed == 0) {
        revert CallerNotCreditManagerException(); // U:[LP-2C,14A]
    }

    if (profit > 0) {
        _mint(treasury, _convertToShares(profit)); // U:[LP-14B]
    } else if (loss > 0) {
        address treasury_ = treasury;
        uint256 sharesInTreasury = balanceOf(treasury_);
        uint256 sharesToBurn = _convertToShares(loss);
        if (sharesToBurn > sharesInTreasury) {
            unchecked {
                emit IncurUncoveredLoss({
                    creditManager: msg.sender,
                    loss: _convertToAssets(sharesToBurn - sharesInTreasury)
                }); // U:[LP-14D]
            }
            sharesToBurn = sharesInTreasury;
        }
        _burn(treasury_, sharesToBurn); // U:[LP-14C,14D]
    }...
}
```

@pkqs90 - Could you please point out the incomplete fix? This is important, since if there is no indication that the sponsor intended to fix it, it would be out of scope (according to this [announcement](https://discord.com/channels/810916927919620096/1293582092533497946/1296431424819298365)).

@Koolex - The 2024-07 code had `pool.repayCreditAccount(debtData.debt, 0, loss);` <https://github.com/code-423n4/2024-07-loopfi/blob/main/src/CDPVault.sol#L624>, and was later fixed to `pool.repayCreditAccount(debtData.debt, profit, loss);` <https://github.com/code-423n4/2024-10-loopfi/blob/main/src/CDPVault.sol#L702>.

The suggested fix was also mentioned the original report for [H-12](https://github.com/code-423n4/2024-07-loopfi-findings/issues/57).
