Audit Report

## Title
Unguarded `sendFunds()` in `FeeReceiver` Enables Front-Running of Large Deposits to Steal Yield - (File: contracts/FeeReceiver.sol)

## Summary

`FeeReceiver.sendFunds()` has no access control, allowing any caller to flush accumulated MEV/execution-layer rewards from `FeeReceiver` into `LRTDepositPool` at will. Combined with the publicly callable `LRTOracle.updateRSETHPrice()`, an attacker holding rsETH can atomically flush rewards and update the rsETH price before a large deposit lands, capturing yield that would otherwise be shared with the incoming depositor.

## Finding Description

`FeeReceiver.sendFunds()` is declared `external` with no role modifier:

```solidity
// contracts/FeeReceiver.sol L53-58
function sendFunds() external {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
```

The destination `LRTDepositPool.receiveFromRewardReceiver()` is equally unguarded:

```solidity
// contracts/LRTDepositPool.sol L61
function receiveFromRewardReceiver() external payable { }
```

Once ETH lands in `LRTDepositPool`, `getETHDistributionData()` immediately counts it as `ethLyingInDepositPool = address(this).balance` (L480), which feeds into `_getTotalEthInProtocol()` in `LRTOracle`, which is consumed by `_updateRsETHPrice()`.

Critically, `LRTOracle.updateRSETHPrice()` is also publicly callable (only `whenNotPaused`, no role check):

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

The rsETH price used for minting is the **stored** `lrtOracle.rsETHPrice()` value (not computed live), so `sendFunds()` alone does not affect minting. However, the attacker can call both `sendFunds()` and `updateRSETHPrice()` in sequence (or atomically via a contract) to:

1. Move accumulated MEV ETH from `FeeReceiver` → `LRTDepositPool`, increasing TVL.
2. Trigger `updateRSETHPrice()`, which recomputes `rsETHPrice` upward from the new TVL.
3. The victim's subsequent `depositETH()` call uses `getRsETHAmountToMint()` → `lrtOracle.rsETHPrice()`, now inflated, minting fewer rsETH tokens for the same ETH.

The `pricePercentageLimit` guard in `_updateRsETHPrice()` (L252-266) only reverts if the price increase exceeds the configured threshold **and** the caller is not a manager. If `pricePercentageLimit == 0` (unset), there is no cap. Even when set, the attacker can exploit any price increase within the limit, and the limit applies per oracle update, not per block.

The comment in `getETHDistributionData()` (L465-466) explicitly confirms that rewards sitting in `FeeReceiver` are **not** counted in TVL until moved, making the price jump discrete and predictable.

## Impact Explanation

**Theft of unclaimed yield — High.**

MEV rewards accumulating in `FeeReceiver` represent yield owed to the protocol's rsETH holders. By flushing and repricing before a large deposit, the attacker ensures that 100% of those accumulated rewards accrue to existing holders (including themselves) rather than being diluted by the incoming depositor. The incoming depositor receives fewer rsETH tokens than they would have if rewards were distributed after their deposit, constituting a direct transfer of yield from the depositor to existing holders. The attacker profits proportionally to their rsETH holdings and the size of the accumulated reward balance.

## Likelihood Explanation

- `sendFunds()` and `updateRSETHPrice()` are both zero-argument, publicly callable functions with no preconditions beyond the oracle not being paused.
- `FeeReceiver` balance is observable on-chain at all times.
- Large `depositETH()` calls are visible in the mempool.
- The attack requires only two sequential public calls; no flash loans, special tokens, or permissions are needed.
- The attack is repeatable every time MEV rewards accumulate to a meaningful level.
- Likelihood is **High**.

## Recommendation

Add an access control modifier to `sendFunds()` restricting it to the manager or operator role:

```solidity
function sendFunds() external onlyRole(LRTConstants.MANAGER) {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
```

Additionally, add a caller check to `LRTDepositPool.receiveFromRewardReceiver()` to ensure it can only be called from the registered `FeeReceiver` address, mirroring the pattern in `NodeDelegator.sendETHFromDepositPoolToNDC()` (L445-451).

## Proof of Concept

1. `FeeReceiver` accumulates 10 ETH in MEV rewards (observable via `address(feeReceiver).balance`).
2. A whale submits `depositETH{value: 1000 ETH}(minRSETHAmountExpected=0)` to `LRTDepositPool`.
3. Attacker (existing rsETH holder) sees the pending transaction and front-runs with a contract that atomically calls:
   - `FeeReceiver.sendFunds()` → 10 ETH moves to `LRTDepositPool`
   - `LRTOracle.updateRSETHPrice()` → rsETH price increases by `10 ETH / totalRsETHSupply`
4. Whale's `depositETH` executes at the inflated `rsETHPrice`, minting fewer rsETH tokens.
5. Attacker's existing rsETH is now worth more ETH per token; the 10 ETH reward was fully captured by pre-existing holders.
6. Foundry fork test: deploy attacker contract, call both functions in one transaction, assert `getRsETHAmountToMint(ETH_TOKEN, 1000 ether)` returns a lower value after the attack than before, and assert attacker's rsETH redemption value increased.