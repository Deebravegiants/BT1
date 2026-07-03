Audit Report

## Title
rsETH Price Inflation via ETH Donation Enables First-Depositor Share Theft - (File: `contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`)

## Summary
`LRTDepositPool` accepts unrestricted ETH via a public `receive()` function, and `getETHDistributionData()` counts `address(this).balance` directly in TVL. Because `updateRSETHPrice()` is public and `pricePercentageLimit` defaults to `0`, an attacker who is the first depositor can donate ETH to inflate `rsETHPrice` without bound. A subsequent depositor who passes `minRSETHAmountExpected = 0` receives 0 rsETH for their deposit, permanently transferring their principal to the attacker.

## Finding Description

**Root cause — donated ETH is counted as protocol TVL.**

`_getTotalEthInProtocol()` in `LRTOracle` iterates over supported assets and calls `ILRTDepositPool.getTotalAssetDeposits(ETH_TOKEN)`, which resolves to `getETHDistributionData()`:

```solidity
// LRTDepositPool.sol L480
ethLyingInDepositPool = address(this).balance;
```

Any ETH sent directly to `LRTDepositPool` via its unrestricted `receive()`:

```solidity
// LRTDepositPool.sol L58
receive() external payable { }
```

is immediately included in the TVL used to compute the new price.

**Price update is public and unguarded by default.**

`updateRSETHPrice()` is callable by any address:

```solidity
// LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

The only price-increase guard is:

```solidity
// LRTOracle.sol L256-257
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```

`pricePercentageLimit` is never assigned in `initialize()`:

```solidity
// LRTOracle.sol L64-68
function initialize(address lrtConfigAddr) external initializer {
    UtilLib.checkNonZeroAddress(lrtConfigAddr);
    lrtConfig = ILRTConfig(lrtConfigAddr);
    emit UpdatedLRTConfig(lrtConfigAddr);
}
```

so it defaults to `0`, making `isPriceIncreaseOffLimit` permanently `false` until an admin calls `setPricePercentageLimit`.

**Minting formula divides by the stored, manipulated price.**

```solidity
// LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

After inflation, a victim's deposit `D` yields `(D * 1e18) / P` which rounds to 0 when `D < P / 1e18`.

**Slippage guard is bypassed when `minRSETHAmountExpected = 0`.**

```solidity
// LRTDepositPool.sol L667-669
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

`0 < 0` is false; the deposit proceeds and the victim receives 0 rsETH.

**Attacker recovers funds through withdrawal.**

`getExpectedAssetAmount` in `LRTWithdrawalManager` also uses the stored `rsETHPrice`:

```solidity
// LRTWithdrawalManager.sol L593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

The attacker, holding 100% of rsETH supply at the inflated price, can withdraw the entire TVL (their donated ETH plus the victim's deposit) through the normal withdrawal queue.

**Precondition on fee configuration.**

`_updateRsETHPrice()` calls `_checkAndUpdateDailyFeeMintLimit`. If `protocolFeeInBPS > 0` and `maxFeeMintAmountPerDay = 0` (both defaults), the call reverts when TVL increases. The attack therefore executes cleanly when `protocolFeeInBPS = 0` (the Solidity default for an unset `uint256` in `LRTConfig`), which is the natural out-of-the-box state.

## Impact Explanation

**Critical — Direct theft of user funds.**

A victim depositing `D` ETH with `minRSETHAmountExpected = 0` after the price has been inflated to `P` receives `floor((D * 1e18) / P)` rsETH. When `D * 1e18 < P`, this is 0 and the victim's entire principal is absorbed into the protocol TVL, which the attacker owns in full via their rsETH position. This matches the allowed impact: *Direct theft of any user funds, whether at-rest or in-motion*.

## Likelihood Explanation

- `pricePercentageLimit = 0` is the default; no admin action is required.
- `protocolFeeInBPS = 0` is the Solidity default for an unset config value, satisfying the fee precondition.
- `minRSETHAmountExpected = 0` is the natural default for users unfamiliar with slippage or for integrations that omit the parameter; it is also the value used when front-running a pending deposit transaction observed in the mempool.
- The attacker must lock capital (donated ETH) but recovers it plus the victim's deposit through the withdrawal path.
- The attack is most effective at protocol launch when rsETH supply is minimal, but is repeatable whenever the attacker can acquire a dominant rsETH share.

## Recommendation

1. **Set `pricePercentageLimit` to a non-zero value in `initialize()`** (e.g., `1e16` for 1%) so that a single public `updateRSETHPrice()` call cannot move the price by more than the configured threshold.
2. **Exclude unaccounted ETH from TVL**, or track deposited ETH separately from `address(this).balance` to prevent direct donations from inflating the price.
3. **Enforce a non-zero minimum rsETH output** in `_beforeDeposit` (e.g., `if (rsethAmountToMint == 0) revert`) regardless of `minRSETHAmountExpected`.
4. **Set `protocolFeeInBPS` and `maxFeeMintAmountPerDay` consistently** during deployment so the fee-limit guard does not silently block price updates in production.

## Proof of Concept

```solidity
// Foundry test outline (fork or local)
function test_priceInflationTheft() public {
    // 1. Attacker deposits 1 wei ETH → receives 1 wei rsETH at price 1e18
    vm.prank(attacker);
    depositPool.depositETH{value: 1}(0, "");

    // 2. Attacker donates 1000 ETH directly to LRTDepositPool
    vm.deal(attacker, 1001 ether);
    vm.prank(attacker);
    (bool ok,) = address(depositPool).call{value: 1000 ether}("");
    assertTrue(ok);

    // 3. Attacker calls updateRSETHPrice() — price inflates to ~1001e18
    vm.prank(attacker);
    lrtOracle.updateRSETHPrice();
    assertGt(lrtOracle.rsETHPrice(), 1000 ether);

    // 4. Victim deposits 1 ETH with minRSETHAmountExpected = 0
    vm.deal(victim, 1 ether);
    vm.prank(victim);
    depositPool.depositETH{value: 1 ether}(0, "");

    // 5. Victim holds 0 rsETH
    assertEq(rsETH.balanceOf(victim), 0);

    // 6. Attacker initiates withdrawal for 1 wei rsETH → expects ~1002 ETH
    vm.prank(attacker);
    withdrawalManager.initiateWithdrawal(ETH_TOKEN, 1, "");
    // After operator unlocks queue, attacker completes withdrawal and recovers 1002 ETH
}
```