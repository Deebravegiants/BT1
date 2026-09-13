# [M] Current logic of the `solvent()` modifier could make users unfairly DOS'd from selling their collateral

## Summary
Severity: Medium
Chain: Smart contract
Component: Tapioca--Lending-Engine-
Published: 2024-06-04
Source: https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/issues/18
Type: hats-finding

## Details
**Github username:** @bauchibred
**Twitter username:** bauchibred
**Submission hash (on-chain):** 0x878ab44dc233f89a7e96c4298f9f4126d3e8745fcea5d3e71d7dc726aa3d08e6
**Severity:** medium

**Description:**
**Description**

Take a look at https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/blob/8920782db6044643fd0c682f58ef37f7e59f99b1/contracts/markets/bigBang/BBLeverage.sol#L133-L170

```solidity
    function sellCollateral(address from, uint256 share, bytes calldata data)
        external
        optionNotPaused(PauseType.LeverageSell)
        solvent(from)
        notSelf(from)
        returns (uint256 amountOut)
    {
        if (address(leverageExecutor) == address(0)) {
            revert LeverageExecutorNotValid();
        }
        penrose.reAccrueBigBangMarkets();

        _allowedBorrow(from, share);
        _removeCollateral(from, address(this), share);

        _SellCollateralMemoryData memory memoryData;

        (memoryData.leverageAmount,) =
            yieldBox.withdraw(collateralId, address(this), address(leverageExecutor), 0, share);
        amountOut =
            leverageExecutor.getAsset(from, address(collateral), address(asset), memoryData.leverageAmount, data);
        memoryData.shareOut = yieldBox.toShare(assetId, amountOut, false);
        address(asset).safeApprove(address(yieldBox), type(uint256).max);
        yieldBox.depositAsset(assetId, address(this), from, 0, memoryData.shareOut); // TODO Check for rounding attack?
        address(asset).safeApprove(address(yieldBox), 0);

        memoryData.partOwed = userBorrowPart[from];
        memoryData.amountOwed = totalBorrow.toElastic(memoryData.partOwed, true);
        memoryData.shareOwed = yieldBox.toShare(assetId, memoryData.amountOwed, true);
        if (memoryData.shareOwed <= memoryData.shareOut) {
            _repay(from, from, memoryData.partOwed, false);
        } else {
            //repay as much as we can
            uint256 partOut = totalBorrow.toBase(amountOut, false);
            _repay(from, from, partOut, false);
        }
        if (amountOut == 0) revert AmountNotValid();
    }
```

This function is used by an integrator in order to sell their collateral so as to repay their debt.

Now there was a [previous finding](https://github.com/sherlock-audit/2024-02-tapioca-judging/issues?q=is%3Aissue+is%3Aopen+hyh+-+Leverage+borrowing+with+stale+rate+can+atomically+create+bad+debt+with+no+prior+positions+and+no+investment+%23) from the sherlock contest about the `solvent()` modifier does not enforce that the exchange rate is always up to date, which is why protocol changed the implementation to the below https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/blob/8920782db6044643fd0c682f58ef37f7e59f99b1/contracts/markets/Market.sol#L167-L175

```solidity
    modifier solvent(address from) {
        updateExchangeRate();
        _accrue();

        _;

        require(_isSolvent(from, exchangeRate, false), "Market: insolvent");
    }

```

https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/blob/8920782db6044643fd0c682f58ef37f7e59f99b1/contracts/markets/Market.sol#L384-L393

```solidity
    function updateExchangeRate() public returns (bool updated, uint256 rate) {
        (updated, rate) = oracle.get(oracleData);
        require(updated, "Market: rate too old");
        require(rate != 0, "Market: invalid rate");

        exchangeRate = rate;
        rateTimestamp = block.timestamp;

        emit LogExchangeRate(rate);
    }
```

Issue however is that, now if there is any issue with getting the exchange rate the whole execution fails, now where as this is logical when someone is trying to enter into the market or so as not game protocol _(since leverage buying, borrow and collateral removal can increase riskiness of a position)_,, that's to say when a user is trying to `borrow()` or `buyCollateral`, this should revert to ensure protocol is safe and they are not being gamed, however in the case of users selling their collateral to repay their debt, this does not increase the risk of a position, so, there should be a check to see that even if updating the exchange rate fails, if the users accept the rate then they should be able to repay their debt, otherwise they could accrue more debt.

This window was also acknowledged in the [linked finding](<(https://github.com/sherlock-audit/2024-02-tapioca-judging/issues?q=is%3Aissue+is%3Aopen+hyh+-+Leverage+borrowing+with+stale+rate+can+atomically+create+bad+debt+with+no+prior+positions+and+no+investment+%23)>), were the auditor hinted that all other instances of using stale rates are acceptable asides the below:

- BBLeverage.buyCollateral()
- BBBorrow.borrow()
- Origins.removeCollateral(), Origins.borrow()
- SGLBorrow.borrow()
- SGLCollateral.removeCollateral()
- SGLLeverage.buyCollateral()

**Attack Scenario**

**Recommendation**
Consider reimplementing the way the `solvent()` modifier exists and how it's being integrated, in the case where it's a function like `sellCollateral()` there mustn't be an enforcal in updating the exchange rate, so consider passing in a `isUpdateRequired()` param to the `solvent()` modifier and in the case where it's a functionality like `sellCollateral` that doesn't increase the risk to a position the `isUpdateRequired()` which would then allow users to be able to access this function and even repay their debts or what not.
**Attachments**

1. **Proof of Concept (PoC) File**

N/A

2. **Revised Code File (Optional)**

N/A
