### Title
Stale Cached `rsETHPrice` Allows Depositors to Receive Excess rsETH, Stealing Yield from Existing Holders — (File: `contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool.getRsETHAmountToMint()` uses `lrtOracle.rsETHPrice()`, a **stale cached value**, to determine how many rsETH to mint per deposit. Because `rsETHPrice` is only updated when `updateRSETHPrice()` is called (which is `public` and permissionless), there is always a window where the cached price underestimates the actual exchange rate. An unprivileged depositor can exploit this window to receive more rsETH than they are entitled to, diluting existing holders' accrued yield.

---

### Finding Description

`LRTOracle` stores `rsETHPrice` as a persistent state variable that is only updated when `_updateRsETHPrice()` is invoked: [1](#0-0) [2](#0-1) 

The actual current exchange rate is computed live inside `_getTotalEthInProtocol()`, which aggregates all assets across the deposit pool, node delegators, EigenLayer strategies, and the unstaking vault: [3](#0-2) 

However, `LRTDepositPool.getRsETHAmountToMint()` does **not** call this live computation. It reads the stale cached `rsETHPrice` directly: [4](#0-3) 

As staking rewards accrue (stETH rebases, EigenLayer rewards, ETH validator rewards), the actual exchange rate rises continuously, but `rsETHPrice` remains frozen at its last-updated value. The discrepancy between the stale cached price and the live rate is the exploitable gap.

`updateRSETHPrice()` is `public` with no access control beyond `whenNotPaused`: [2](#0-1) 

This means any caller can atomically:
1. Deposit at the stale (lower) `rsETHPrice` → receive `amount * assetPrice / rsETHPrice_stale` rsETH (inflated)
2. Call `updateRSETHPrice()` in the same or next transaction → `rsETHPrice` jumps to the actual higher rate
3. Request withdrawal using the now-higher `rsETHPrice` → receive more assets than deposited

The withdrawal manager reads `lrtOracle.rsETHPrice()` at unlock time to compute the asset amount owed: [5](#0-4) 

So the attacker's inflated rsETH balance is redeemed at the post-update (higher) price, extracting value from existing holders.

The `_updateRsETHPrice()` function computes the new price as: [6](#0-5) 

When the attacker's inflated rsETH is included in `rsethSupply` before the price update, the new price is diluted — existing holders' share of the TVL is reduced.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Existing rsETH holders continuously accrue yield as the underlying assets (stETH, ETHx, EigenLayer rewards) appreciate. This yield is reflected in the rising actual exchange rate but is not yet captured in the stale `rsETHPrice`. A depositor who enters at the stale price receives a larger share of the total rsETH supply than the actual TVL justifies. When `updateRSETHPrice()` is called, the new price is computed over a larger rsETH supply, permanently diluting the yield that existing holders had accrued since the last price update. The attacker exits with more assets than they deposited; the loss is borne by all existing rsETH holders proportionally.

---

### Likelihood Explanation

**Medium.**

- `rsETHPrice` is updated by off-chain bots on a periodic schedule. Any gap between updates (routine or due to bot failure, network congestion, or gas spikes) creates the exploitable window.
- `updateRSETHPrice()` is permissionless, so the attacker does not need to wait for the bot — they can trigger the update themselves immediately after depositing.
- The `pricePercentageLimit` check can revert non-manager callers if the price jump is too large, but: (a) if `pricePercentageLimit == 0` there is no cap; (b) for moderate reward accrual periods the increase will be within the limit; (c) the attacker can also simply wait for the bot to update the price rather than calling it themselves.
- No special privileges are required. Any EOA or contract can call `depositETH()` and `updateRSETHPrice()`.

---

### Recommendation

Compute the rsETH mint amount using the **live** exchange rate rather than the stale cached `rsETHPrice`. Specifically, `getRsETHAmountToMint()` should call `_getTotalEthInProtocol()` (or an equivalent live computation) and divide by `rsethSupply` to derive the current rate on-the-fly, rather than reading `rsETHPrice` from storage. Alternatively, atomically call `updateRSETHPrice()` at the start of every deposit transaction so the cached price is always fresh before minting.

---

### Proof of Concept

```
Setup:
  - rsETHPrice (cached) = 1.00 ETH  (last updated T=0)
  - Actual TVL / rsETH supply       = 1.05 ETH  (rewards accrued since T=0)
  - Existing holder Alice holds 100 rsETH

Attack (at T=1, before next bot update):
  1. Attacker deposits 100 ETH via depositETH().
     rsethAmountToMint = 100 ETH * 1e18 / 1.00e18 = 100 rsETH   ← inflated
     (correct amount would be 100 / 1.05 ≈ 95.24 rsETH)

  2. Attacker calls updateRSETHPrice().
     New TVL = 205 ETH (100 deposited + 105 existing)
     New rsETH supply = 200 rsETH (100 Alice + 100 attacker)
     newRsETHPrice = 205 / 200 = 1.025 ETH   ← diluted from 1.05

  3. Attacker requests withdrawal of 100 rsETH.
     After delay, asset returned = 100 * 1.025 = 102.5 ETH

  Attacker profit: +2.5 ETH
  Alice's loss: her 100 rsETH is now worth 102.5 ETH instead of 105 ETH
                → 2.5 ETH of Alice's accrued yield stolen
```

### Citations

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

**File:** contracts/LRTOracle.sol (L249-251)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
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

**File:** contracts/LRTWithdrawalManager.sol (L841-851)
```text
    )
        internal
        view
        returns (UnlockParams memory)
    {
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
    }
```
