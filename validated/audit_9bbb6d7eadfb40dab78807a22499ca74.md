### Title
Publicly Callable `updateRSETHPrice()` Enables Selective Price-Update Timing to Steal Yield from rsETH Holders — (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is callable by anyone with no access control. The `rsETHPrice` it stores is a stale cached value used verbatim by both `LRTDepositPool` (for minting) and `LRTWithdrawalManager` (for withdrawal sizing). `FeeReceiver.sendFunds()` is also publicly callable and moves accumulated MEV/execution-layer rewards into the deposit pool, increasing TVL without updating the price. Any user can observe the pending price increase off-chain, deposit at the stale (lower) price, then atomically trigger the price update — capturing a share of rewards that should belong to existing rsETH holders.

---

### Finding Description

`LRTOracle.updateRSETHPrice()` carries no role guard:

```solidity
// contracts/LRTOracle.sol:87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

The stored `rsETHPrice` is the only value consulted at deposit time:

```solidity
// contracts/LRTDepositPool.sol:519-520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

And at withdrawal-initiation time:

```solidity
// contracts/LRTWithdrawalManager.sol:592-593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

`FeeReceiver.sendFunds()` is also unrestricted:

```solidity
// contracts/FeeReceiver.sol:53-57
function sendFunds() external {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
```

The internal price update computes the reward as `totalETHInProtocol − previousTVL`, where `previousTVL = rsethSupply × rsETHPrice`:

```solidity
// contracts/LRTOracle.sol:234,244-246
uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);
...
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
```

Because the attacker's deposit increases `rsethSupply` before the price update, the `previousTVL` baseline rises, which reduces the computed `rewardAmount` attributed to existing holders. The attacker's newly minted rsETH participates in the price appreciation as if they had been a holder before the rewards arrived.

The `pricePercentageLimit` guard only reverts if the price increase exceeds the configured threshold; it does not prevent the attack when rewards are within that band, and it is entirely absent when `pricePercentageLimit == 0`.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Existing rsETH holders accumulate yield through staking rewards and MEV fees. An attacker who deposits just before triggering the price update dilutes those holders' share of the pending reward. The attacker exits with more ETH than they deposited; the shortfall comes directly from yield owed to pre-existing holders. The attack scales linearly with the size of the deposit and the magnitude of accumulated rewards.

---

### Likelihood Explanation

**Medium.** MEV/execution-layer rewards accumulate in `FeeReceiver` continuously and are publicly visible on-chain. Staking rewards increase `getEffectivePodShares()` automatically over time. No privileged role is required. The only friction is the 8-day withdrawal delay, which does not prevent the attack — it merely defers the profit. The `pricePercentageLimit` guard reduces per-transaction profit but does not eliminate the attack, and it is bypassable when the limit is unset.

---

### Recommendation

1. **Atomically refresh the price on every deposit and withdrawal.** Call `_updateRsETHPrice()` (or an equivalent snapshot) at the start of `depositETH`, `depositAsset`, and `initiateWithdrawal` so the price used for minting/sizing always reflects the current TVL.
2. **Restrict `FeeReceiver.sendFunds()` to an authorized role** (e.g., `MANAGER`) so that reward injection cannot be weaponised as part of a sandwich.
3. As a defence-in-depth measure, enforce a minimum deposit lock-up period so that same-block deposit-then-withdraw cycles are impossible.

---

### Proof of Concept

**Setup:**
- Protocol TVL = 10 000 ETH; rsETH supply = 10 000; `rsETHPrice` = 1.0 ETH (stale).
- `FeeReceiver` holds 100 ETH in accumulated MEV rewards (not yet moved to the deposit pool).
- Protocol fee = 10 %.

**Attack steps:**

1. Attacker calls `LRTDepositPool.depositETH{value: 1000 ETH}(...)`.
   - `rsethAmountToMint = 1000 × 1.0 / 1.0 = 1000 rsETH` (stale price used).
   - New supply = 11 000 rsETH; TVL = 11 000 ETH; `rsETHPrice` still = 1.0.

2. Attacker calls `FeeReceiver.sendFunds()`.
   - 100 ETH moves to deposit pool; TVL = 11 100 ETH.

3. Attacker calls `LRTOracle.updateRSETHPrice()`.
   - `previousTVL = 11 000 × 1.0 = 11 000 ETH`.
   - `rewardAmount = 11