Audit Report

## Title
Stale `rsETHPrice` Cache in Deposit Minting Allows Depositors to Dilute Existing Holders' Yield - (File: contracts/LRTDepositPool.sol)

## Summary
`LRTDepositPool.getRsETHAmountToMint()` divides a live Chainlink asset price by `lrtOracle.rsETHPrice()`, a state variable that is only refreshed when `updateRSETHPrice()` is called in a separate transaction. As staking rewards accrue and the cached price lags behind the true value, any depositor can mint more rsETH than their deposit warrants, permanently diluting the yield accrued by existing holders.

## Finding Description
`getRsETHAmountToMint` computes the mint amount as:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [1](#0-0) 

`lrtOracle.getAssetPrice(asset)` is a live read through `IPriceFetcher`, while `lrtOracle.rsETHPrice()` is a plain public state variable: [2](#0-1) [3](#0-2) 

`rsETHPrice` is only written inside `_updateRsETHPrice()`, which is invoked by the permissionless `updateRSETHPrice()` or the manager-only `updateRSETHPriceAsManager()`: [4](#0-3) [5](#0-4) 

The full deposit path — `depositETH` → `_beforeDeposit` → `getRsETHAmountToMint` — contains no call to `updateRSETHPrice()` and no staleness check: [6](#0-5) [7](#0-6) 

Compounding the issue, `_updateRsETHPrice()` contains a `pricePercentageLimit` guard that reverts for non-managers when the price increase exceeds the configured threshold: [8](#0-7) 

This means that during periods of significant reward accrual — precisely when the staleness gap is largest — permissionless callers cannot refresh the price at all, extending the window of exploitability.

## Impact Explanation
When `rsETHPrice` is stale and lower than the true current value, the denominator in `getRsETHAmountToMint` is artificially small, causing the depositor to receive excess rsETH. When `updateRSETHPrice()` is eventually called, the new price is computed as `(totalETHInProtocol - fee) / rsethSupply`; because the supply was inflated by the excess mint, the price per rsETH is permanently lower than it would have been, directly reducing the redemption value of every pre-existing holder's position. This constitutes **theft of unclaimed yield** (High impact) from existing rsETH holders. [9](#0-8) 

## Likelihood Explanation
- `updateRSETHPrice()` is a separate call with no on-chain enforcement that it must precede deposits; the staleness window opens naturally between keeper calls.
- Staking rewards and LST appreciation accrue continuously, so the gap between `rsETHPrice` and the true price grows over time.
- The `pricePercentageLimit` guard actively blocks permissionless updates during high-reward periods, widening the exploitable window.
- Any unprivileged depositor can compare the on-chain `rsETHPrice` against a locally computed `_getTotalEthInProtocol() / rsethSupply` to identify and time the attack with zero capital risk beyond gas.

## Recommendation
Force a price refresh before computing the mint amount. Either:
1. Call `lrtOracle.updateRSETHPrice()` at the start of `depositETH` / `depositAsset` (requires making `_updateRsETHPrice` non-reverting for non-managers when the limit is exceeded, or using a try/catch), or
2. Expose a pure view function in `LRTOracle` that computes `(_getTotalEthInProtocol() - fee) / rsethSupply` without writing state, and use that value as the denominator in `getRsETHAmountToMint` instead of the cached `rsETHPrice`.

## Proof of Concept
1. Staking rewards accrue; `_getTotalEthInProtocol()` grows so the true rsETH price is 1.001 ETH, but `rsETHPrice` is still stored as 1.000 ETH.
2. `updateRSETHPrice()` has not been called (or is blocked by `pricePercentageLimit` for non-managers).
3. Attacker calls `depositETH(minRSETHAmountExpected, "")` with 100 ETH.
4. `getRsETHAmountToMint` computes: `(100e18 * 1e18) / 1.000e18 = 100 rsETH` instead of the correct `(100e18 * 1e18) / 1.001e18 ≈ 99.9 rsETH`.
5. Attacker receives ~0.1 rsETH excess extracted from existing holders' accrued yield.
6. When `updateRSETHPrice()` is eventually called, the inflated supply lowers the price for all holders.

**Foundry fork test plan:** Fork mainnet, advance time to accumulate rewards, verify `rsETHPrice < _getTotalEthInProtocol() / rsethSupply`, call `depositETH` as an unprivileged address, assert the minted rsETH exceeds the fair-value amount, then call `updateRSETHPrice()` and assert the post-update price per rsETH is lower than it would have been without the stale-price deposit.

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L249-251)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTOracle.sol (L260-265)
```text
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```
