Audit Report

## Title
Stale `rsETHPrice` Broadcast Cross-Chain via Permissionless `updateRate()` When Price Exceeds Threshold Guard - (`contracts/cross-chain/MultiChainRateProvider.sol`)

## Summary
`RSETHMultiChainRateProvider.getLatestRate()` reads the stored `rsETHPrice` state variable from `LRTOracle` directly. When a legitimate price increase exceeds `pricePercentageLimit`, `_updateRsETHPrice()` reverts for non-managers, leaving `rsETHPrice` at the pre-increase value. Because `updateRate()` carries no access control, any caller can immediately broadcast this stale, underpriced rate to all registered destination chains via LayerZero.

## Finding Description
The call chain is confirmed by the code:

`updateRate()` (no role check, only `nonReentrant`) → `getLatestRate()` → `ILRTOracle(rsETHPriceOracle).rsETHPrice()`

`RSETHMultiChainRateProvider.getLatestRate()` reads the stored state variable unconditionally: [1](#0-0) 

`updateRate()` has no access control beyond reentrancy protection: [2](#0-1) 

`rsETHPrice` is only written at the very end of `_updateRsETHPrice()`: [3](#0-2) 

Before that write, when the new price exceeds `highestRsethPrice` by more than `pricePercentageLimit`, non-managers hit a hard revert: [4](#0-3) 

Because the revert occurs before line 313, `rsETHPrice` remains at the old lower value. Any unprivileged caller can then invoke `updateRate()`, which reads this stale value and sends it to every `RSETHRateReceiver` via LayerZero. The manager's corrective path (`updateRSETHPriceAsManager()`) is the only way to advance `rsETHPrice`, but there is no mechanism preventing the stale rate from being broadcast in the interim.

## Impact Explanation
Destination chain pools that consume the received rate to price rsETH/ETH deposits will see an artificially low rate. Users depositing ETH on destination chains receive more rsETH per ETH than the true exchange rate warrants, diluting existing rsETH holders' share of protocol TVL. This matches **Low — contract fails to deliver promised returns, but doesn't lose value** from the allowed impact scope.

## Likelihood Explanation
The precondition — a TVL/reward accrual event that pushes the computed price above `pricePercentageLimit` — is a routine operational occurrence (e.g., a large staking reward epoch). The attack window opens the moment a non-manager's `updateRSETHPrice()` call reverts and closes only when the manager calls `updateRSETHPriceAsManager()`. During this window, `updateRate()` is permissionless and costs only gas plus LayerZero fees, making it trivially executable by any EOA or bot.

## Recommendation
The most targeted fix is to have `RSETHMultiChainRateProvider.getLatestRate()` recompute the price on-the-fly (calling a view function that mirrors `_getTotalEthInProtocol()` logic) rather than reading the potentially stale stored `rsETHPrice`. Alternatively, gate `updateRate()` behind the same manager role required when the price is above the threshold, or add a consistency check inside `updateRate()` that attempts `updateRSETHPrice()` first and only proceeds if it does not revert.

## Proof of Concept
```
1. Deploy LRTOracle and RSETHMultiChainRateProvider; set pricePercentageLimit = 1e16 (1%).
2. Record preIncreasePrice = lrtOracle.rsETHPrice().
3. Mock asset oracle to return a price 2% higher, increasing computed rsETH price by 2%.
4. Call lrtOracle.updateRSETHPrice() as an unprivileged EOA → expect revert PriceAboveDailyThreshold.
5. Assert lrtOracle.rsETHPrice() == preIncreasePrice (state unchanged).
6. Call rsETHMultiChainRateProvider.updateRate{value: fee}() as the same EOA → succeeds.
7. Assert the emitted RateUpdated event carries preIncreasePrice, not the true higher price.
8. On the destination chain mock (RSETHRateReceiver), assert the received rate == preIncreasePrice.
```

The stale rate is provably the pre-increase value because `rsETHPrice` is never written when `_updateRsETHPrice()` reverts at line 264, and `getLatestRate()` reads only that stored variable at line 27. [5](#0-4) [1](#0-0)

### Citations

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-111)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;
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
