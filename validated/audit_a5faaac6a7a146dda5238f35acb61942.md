I need to read the key functions more carefully to trace the exact math and check all guards.

### Title
Stale-Price Front-Run on `updateRSETHPrice()` Allows Theft of Pending Yield — (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is an unrestricted `public` function. Because `LRTDepositPool.depositETH()` mints rsETH at the **stored** (stale) `rsETHPrice`, an attacker who observes reward ETH land in the deposit pool before the price is updated can deposit at the old lower price, call `updateRSETHPrice()` themselves, and initiate a withdrawal at the new higher price — locking in a profit equal to their pro-rata share of the reward that they never earned.

The claimed impact of **protocol insolvency** is not accurate. The correct impact is **High — Theft of unclaimed yield**: existing rsETH holders lose a portion of the pending reward to the attacker.

---

### Finding Description

**Entrypoint 1 — unrestricted price update** [1](#0-0) 

`updateRSETHPrice()` carries only `whenNotPaused`; any EOA or contract can call it at any time.

**Entrypoint 2 — deposit uses stored (stale) price** [2](#0-1) 

`getRsETHAmountToMint` divides by `lrtOracle.rsETHPrice()` — the last *written* value, not a freshly computed one. If reward ETH has arrived in the pool but the price has not been updated, this value is stale.

**Entrypoint 3 — withdrawal locks in the post-update price** [3](#0-2) 

`getExpectedAssetAmount` multiplies by `lrtOracle.rsETHPrice()` at initiation time and stores the result as `expectedAssetAmount`.

**Unlock-time payout cap** [4](#0-3) 

`_calculatePayoutAmount` returns `min(expectedAssetAmount, currentReturn)`. This protects against price *increases* after initiation, but does **not** undo the profit already locked in at initiation when the attacker used the post-update price.

**`_updateRsETHPrice` reward accounting** [5](#0-4) 

`previousTVL` is computed as `rsethSupply × rsETHPrice`. After the attacker deposits D ETH at the stale price P₁ = T/S, `rsethSupply` grows to S + D·S/T, so `previousTVL` = T + D. The reward R = `totalETHInProtocol − previousTVL` = (T+D+R) − (T+D) = R is correctly identified, but the new price P₂ = (T+D+R)·T / (S·(T+D)) is now diluted by the attacker's deposit, and the attacker holds more rsETH than they should at that price.

---

### Impact Explanation

Let:
- T = TVL before reward, S = rsETH supply, P₁ = T/S (stored price)
- R = reward ETH already in pool, D = attacker deposit

Attacker mints at P₁: `rsETH_attacker = D·S/T`  
Correct mint (at true price (T+R)/S): `rsETH_correct = D·S/(T+R)`  
Excess rsETH: `D·S·R / (T·(T+R))`

After `updateRSETHPrice()`, P₂ = (T+D+R)·T / (S·(T+D)).  
Attacker's `expectedAssetAmount` = `rsETH_attacker × P₂` = D·(T+D+R)/(T+D)  
Attacker profit = D·R/(T+D)

This profit is extracted from existing rsETH holders, who each lose `R·D / (S·(T+D))` ETH per rsETH. This is **theft of unclaimed yield**, not protocol insolvency — the protocol remains solvent.

---

### Likelihood Explanation

- `updateRSETHPrice()` has no access control; any attacker can call it.
- Reward ETH regularly arrives in `LRTDepositPool` via `receive()` / `receiveFromRewardReceiver()` before the off-chain keeper calls the price update.
- The only partial mitigations are: (a) `pricePercentageLimit` — reverts if the price jump exceeds the configured threshold for non-managers, limiting the exploitable reward size per call; (b) the 8-day `withdrawalDelayBlocks` — delays profit realization but does not prevent it, since `expectedAssetAmount` is locked in at initiation.
- No admin compromise, governance capture, or oracle manipulation is required.

---

### Recommendation

1. **Restrict `updateRSETHPrice()`** to a trusted keeper role (e.g., `onlyLRTManager` or a dedicated `PRICE_UPDATER_ROLE`). The current `updateRSETHPriceAsManager()` already exists for privileged updates; the public variant should be removed or similarly gated.
2. **Alternatively**, compute rsETH-to-mint using a freshly calculated price (calling `_getTotalEthInProtocol()` inline) rather than the stored `rsETHPrice`, so a stale stored value cannot be exploited.
3. Ensure `pricePercentageLimit` is always set to a non-zero value as a defence-in-depth measure.

---

### Proof of Concept

```solidity
// Foundry fork test (local fork, no public-mainnet calls)
function testSandwichYieldTheft() public {
    // Setup: T = 1000 ETH TVL, S = 1000 rsETH, P1 = 1e18
    // Reward: 10 ETH sent to depositPool (price not yet updated)
    vm.deal(address(depositPool), address(depositPool).balance + 10 ether);

    uint256 D = 100 ether;
    vm.deal(attacker, D);

    // Step 1: deposit at stale price P1
    vm.prank(attacker);
    depositPool.depositETH{value: D}(0, "");
    uint256 rsETHReceived = rsETH.balanceOf(attacker);
    // rsETHReceived = 100e18 (100 rsETH at P1=1e18)

    // Step 2: attacker calls updateRSETHPrice — no access control
    vm.prank(attacker);
    lrtOracle.updateRSETHPrice();
    // P2 = (1000+100+10)*1e18 / (1000+100) ≈ 1.00909e18

    // Step 3: initiate withdrawal at P2
    vm.prank(attacker);
    rsETH.approve(address(withdrawalManager), rsETHReceived);
    vm.prank(attacker);
    withdrawalManager.initiateWithdrawal(ETH_TOKEN, rsETHReceived, "");
    // expectedAssetAmount ≈ 100.909 ETH

    // Step 4: fast-forward 8 days, operator unlocks, attacker completes
    vm.roll(block.number + withdrawalManager.withdrawalDelayBlocks() + 1);
    // ... operator calls unlockQueue, attacker calls completeWithdrawal

    uint256 received = attacker.balance;
    assertGt(received, D); // attacker receives > 100 ETH deposited
    // profit ≈ 100 * 10 / (1000+100) ≈ 0.909 ETH stolen from existing holders
}
``` [1](#0-0) [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L231-250)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L166-175)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L580-594)
```text
    function getExpectedAssetAmount(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 underlyingToReceive)
    {
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L824-835)
```text
    function _calculatePayoutAmount(
        WithdrawalRequest storage request,
        uint256 rsETHPrice,
        uint256 assetPrice
    )
        private
        view
        returns (uint256)
    {
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
    }
```
