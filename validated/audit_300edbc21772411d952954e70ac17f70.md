### Title
Donation Attack via `balanceOf` in `getAssetDistributionData`/`getETHDistributionData` Inflates `rsETHPrice`, Causing Future Depositors to Receive Zero rsETH - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool.getAssetDistributionData` and `getETHDistributionData` compute total protocol TVL using raw `balanceOf` / `address.balance` reads. An attacker can donate LST tokens or ETH directly to `LRTDepositPool`, `NodeDelegator`, or `LRTUnstakingVault` without going through the deposit function. After calling the public `updateRSETHPrice()`, the inflated TVL is baked into `rsETHPrice`. Future depositors then receive fewer rsETH tokens than they should — down to zero — while the attacker, as the sole rsETH holder, can withdraw all protocol assets including the victims' deposits.

---

### Finding Description

**Root cause — `getAssetDistributionData` (LST path):** [1](#0-0) 

`assetLyingInDepositPool`, `assetLyingInNDCs`, and `assetLyingUnstakingVault` are all read from `IERC20(asset).balanceOf(...)`. Any tokens transferred directly to these contracts — without calling `depositAsset` — are silently counted as protocol TVL.

**Root cause — `getETHDistributionData` (ETH path):** [2](#0-1) 

`address(this).balance` and `nodeDelegatorQueue[i].balance` are raw ETH balances. `LRTDepositPool` has an open `receive()` payable fallback, so ETH can be force-sent. [3](#0-2) 

**Price propagation — `_updateRsETHPrice`:** [4](#0-3) 

`_getTotalEthInProtocol` calls `getTotalAssetDeposits` → `getAssetDistributionData`. The inflated total is divided by `rsethSupply` to produce `newRsETHPrice`. `updateRSETHPrice()` is public and callable by anyone.

**Mint calculation — `getRsETHAmountToMint`:** [5](#0-4) 

`rsethAmountToMint = (amount * assetPrice) / rsETHPrice`. A sufficiently inflated `rsETHPrice` truncates this to zero.

**Price-increase guard is disabled by default:** [6](#0-5) 

`isPriceIncreaseOffLimit` is `false` whenever `pricePercentageLimit == 0`. The storage variable is never set in `initialize`, so it defaults to zero. With no guard, a single large donation can inflate the price by any factor in one transaction.

---

### Impact Explanation

**Critical — direct theft of user funds.**

Attack sequence at protocol inception (small rsETH supply):

1. Attacker deposits `minAmountToDeposit` of stETH → receives `S` rsETH (attacker owns 100% of supply).
2. Attacker transfers `D` stETH directly to `LRTDepositPool` (no deposit, no rsETH minted).
3. Attacker calls `updateRSETHPrice()`. New price: `(S_eth + D) * 1e18 / S`. With `D >> S_eth`, price becomes enormous.
4. Victim deposits `B` stETH. `rsethAmountToMint = B * 1e18 / huge_price = 0`. Victim receives 0 rsETH; their `B` stETH is now in the pool.
5. Attacker initiates withdrawal of all `S` rsETH. They redeem `S * newPrice / assetPrice ≈ S_eth + D + B` stETH — recovering the donation **and** stealing the victim's `B` stETH.

Net attacker profit: `B` stETH (victim's entire deposit).

---

### Likelihood Explanation

**Medium-High.** The attack is most effective at protocol inception when rsETH supply is small. `updateRSETHPrice()` is permissionless. `pricePercentageLimit` defaults to zero, removing the only guard. The attacker needs capital equal to the donation `D`, but recovers it in full during withdrawal, so the net cost is only the initial deposit (which is also recovered). The attack is atomic and requires no privileged access.

---

### Recommendation

Track asset balances internally with a dedicated storage variable incremented on deposit and decremented on withdrawal/transfer-out, rather than relying on `balanceOf`. Replace:

```solidity
assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
```

with a mapping `internalBalance[asset]` updated only through controlled entry points. Apply the same fix to `ethLyingInDepositPool` (use a tracked variable instead of `address(this).balance`). Additionally, ensure `pricePercentageLimit` is set to a non-zero value during initialization to bound single-step price manipulation.

---

### Proof of Concept

```
State: rsETH supply = 0, rsETHPrice = 1e18 (bootstrap), stETH assetPrice = 1e18

Step 1 — Attacker deposits 1e18 stETH via depositAsset():
  rsethAmountToMint = 1e18 * 1e18 / 1e18 = 1e18
  rsETH supply = 1e18, attacker owns 100%

Step 2 — Attacker transfers 1e36 stETH directly to LRTDepositPool (no deposit call):
  IERC20(stETH).transfer(address(lrtDepositPool), 1e36)
  getTotalAssetDeposits(stETH) = 1e18 + 1e36 ≈ 1e36

Step 3 — Attacker calls updateRSETHPrice() (public, no access control):
  totalETHInProtocol ≈ 1e36
  newRsETHPrice = 1e36 * 1e18 / 1e18 = 1e36
  rsETHPrice = 1e36  (pricePercentageLimit == 0, no revert)

Step 4 — Victim deposits 1e18 stETH via depositAsset():
  rsethAmountToMint = 1e18 * 1e18 / 1e36 = 0
  → MinimumAmountToReceiveNotMet reverts only if minRSETHAmountExpected > 0;
    if victim passes 0 as minRSETHAmountExpected, tx succeeds and victim gets 0 rsETH.
  Victim's 1e18 stETH is now in the pool.

Step 5 — Attacker withdraws 1e18 rsETH:
  underlyingToReceive = 1e18 * 1e36 / 1e18 = 1e36 stETH
  Attacker recovers donation + victim deposit.
  Net profit = 1e18 stETH (victim's deposit).
```

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L444-461)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));

        uint256 ndcsCount = nodeDelegatorQueue.length;
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);

            unchecked {
                ++i;
            }
        }

        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);

        assetLyingInConverter = 0; // assets in converter are accounted in their eth value => getETHDistributionData()
        assetLyingUnstakingVault = IERC20(asset).balanceOf(lrtUnstakingVault);
```

**File:** contracts/LRTDepositPool.sol (L480-496)
```text
        ethLyingInDepositPool = address(this).balance;

        uint256 ndcsCount = nodeDelegatorQueue.length;

        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }

        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
        ethLyingInUnstakingVault = lrtUnstakingVault.balance;
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```
