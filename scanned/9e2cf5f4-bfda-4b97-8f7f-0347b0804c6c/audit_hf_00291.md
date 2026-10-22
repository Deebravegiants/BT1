# [M] `investedAssets

## Summary
Severity: Medium
Contest weight: 0.5334
Dataset id: 1467
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `investedAssets()` function is implemented by the vault’s strategy contracts as a way to express a vault’s investments in terms of the underlying currency. While the implementation of this function in `BaseStrategy.sol` and `NonUSTStrategy.sol` is mostly correct. It does not account for the performance fee charged by the treasury as shown in `finishRedeemStable()`.

Therefore, an attacker could avoid paying their fair share of the performance fee by withdrawing their assets before several calls to `finishRedeemStable()` are made and reenter the vault once the fee is charged.

## Proof of Concept
```solidity
function finishRedeemStable(uint256 idx) public virtual {
        require(redeemOperations.length > idx, "not running");
        Operation storage operation = redeemOperations[idx];
        uint256 aUstBalance = _getAUstBalance() + pendingRedeems;
        uint256 originalUst = (convertedUst * operation.amount) / aUstBalance;
        uint256 ustBalanceBefore = _getUstBalance();
    
        ethAnchorRouter.finishRedeemStable(operation.operator);
    
        uint256 redeemedAmount = _getUstBalance() - ustBalanceBefore;
        uint256 perfFee = redeemedAmount > originalUst
            ? (redeemedAmount - originalUst).percOf(perfFeePct)
            : 0;
        if (perfFee > 0) {
            ustToken.safeTransfer(treasury, perfFee);
            emit PerfFeeClaimed(perfFee);
        }
        convertedUst -= originalUst;
        pendingRedeems -= operation.amount;
    
        operation.operator = redeemOperations[redeemOperations.length - 1]
            .operator;
        operation.amount = redeemOperations[redeemOperations.length - 1].amount;
        redeemOperations.pop();
    }

    function investedAssets()
        external
        view
        virtual
        override(IStrategy)
        returns (uint256)
    {
        uint256 underlyingBalance = _getUnderlyingBalance() + pendingDeposits;
        uint256 aUstBalance = _getAUstBalance() + pendingRedeems;
    
        return
            underlyingBalance +
            ((exchangeRateFeeder.exchangeRateOf(address(aUstToken), true) *
                aUstBalance) / 1e18);
    }

    function investedAssets()
        external
        view
        override(BaseStrategy)
        returns (uint256)
    {
        uint256 underlyingBalance = _getUnderlyingBalance();
        uint256 aUstBalance = _getAUstBalance() + pendingRedeems;
    
        uint256 ustAssets = ((exchangeRateFeeder.exchangeRateOf(
            address(aUstToken),
            true
        ) * aUstBalance) / 1e18) + pendingDeposits;
        return
            underlyingBalance +
            curvePool.get_dy_underlying(ustI, underlyingI, ustAssets);
    }
```

## Recommendation
When calculating the `investedAssets()` amount (expressed in the underlying currency), consider calculating the expected performance fee to be charged if all the strategy’s assets are withdrawn from the Anchor protocol. This should ensure that `investedAssets()` returns the most accurate amount, preventing users from gaming the protocol.
