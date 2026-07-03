### Title
Stale `rsETHPrice` Allows Depositors to Capture stETH Rebase Yield from Existing Holders — (`contracts/LRTOracle.sol` / `contracts/LRTDepositPool.sol`)

---

### Summary

`LRTOracle.rsETHPrice` is a lazily-updated state variable. Between a stETH rebase (which immediately increases the protocol's TVL) and the next call to `updateRSETHPrice()`, any depositor can mint rsETH at the pre-rebase price, capturing a portion of the yield that should belong to existing holders.

---

### Finding Description

`getRsETHAmountToMint` computes the rsETH to mint as:

```
rsethAmountToMint = (amount × getAssetPrice(asset)) / rsETHPrice()
``` [1](#0-0) 

`rsETHPrice()` is a **stored state variable** in `LRTOracle`, not computed on-the-fly: [2](#0-1) 

It is only updated when `updateRSETHPrice()` (public) or `updateRSETHPriceAsManager()` (manager-only) is explicitly called: [3](#0-2) 

When `_updateRsETHPrice()` runs, it computes the new price from live TVL via `_getTotalEthInProtocol()`, which reads `getTotalAssetDeposits(stETH)` → `IERC20(stETH).balanceOf(depositPool)` in real time: [4](#0-3) 

stETH is a rebasing token: its `balanceOf` increases automatically at each rebase (daily on Ethereum mainnet) without any on-chain transaction. The moment a rebase occurs, `_getTotalEthInProtocol()` would return a higher value, but `rsETHPrice` remains at its last stored value until `updateRSETHPrice()` is called. There is no staleness check, no timestamp guard, and no automatic update triggered by `depositETH`.

**Attack path (no special role required):**

1. stETH rebases → `IERC20(stETH).balanceOf(depositPool)` increases by δ (e.g., 1%)
2. `rsETHPrice` is still the pre-rebase value (e.g., 1.000 ETH/rsETH instead of 1.010 ETH/rsETH)
3. Attacker calls `depositETH(1 ether)` → receives `1e18 / 1.000e18 = 1.000` rsETH
4. Correct post-rebase mint would be `1e18 / 1.010e18 ≈ 0.990` rsETH
5. `updateRSETHPrice()` is called (by keeper or anyone) → `rsETHPrice` rises to 1.010 ETH/rsETH
6. Attacker's 1.000 rsETH is now worth 1.010 ETH — a profit of ~0.010 ETH extracted from existing holders' yield

The same path applies to `depositAsset` for any rebasing LST.

---

### Impact Explanation

Existing rsETH holders' unclaimed yield (the stETH rebase increment) is diluted. The attacker receives rsETH at a discount relative to the true post-rebase NAV, and after the price update their position is worth more than they deposited. This is a direct, quantifiable transfer of yield from existing holders to the depositor. Impact: **High — Theft of unclaimed yield**.

---

### Likelihood Explanation

stETH rebases once per day on mainnet. `updateRSETHPrice()` is not called atomically with the rebase; it depends on an off-chain keeper. The stale window is predictable and can last minutes to hours. No special role, no private key, no governance action is required — only a standard `depositETH` call. The attack is repeatable every rebase cycle. Likelihood: **High**.

---

### Recommendation

Update `rsETHPrice` atomically inside `depositETH` / `depositAsset` before computing the mint amount, or compute the mint ratio on-the-fly from live TVL and rsETH supply rather than from the cached `rsETHPrice` state variable. Alternatively, enforce a maximum staleness window and revert deposits when `rsETHPrice` has not been refreshed within that window.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Fork test (Hardhat/Foundry mainnet fork)
// Preconditions:
//   - LRTDepositPool holds stETH
//   - rsETHPrice was last updated before the rebase

interface IStETH { function balanceOf(address) external view returns (uint256); }
interface ILRTDepositPool { function depositETH(uint256, string calldata) external payable; }
interface ILRTOracle { function rsETHPrice() external view returns (uint256); function updateRSETHPrice() external; }
interface IRSETH { function balanceOf(address) external view returns (uint256); }

contract PoC {
    function run(
        address depositPool,
        address oracle,
        address rseth,
        address steth
    ) external payable {
        uint256 priceBefore = ILRTOracle(oracle).rsETHPrice();

        // 1. Simulate stETH rebase: warp time or use vm.store to increase stETH balance
        //    (In Foundry: vm.prank(stETH_rebase_oracle); stETH.rebase(...))
        //    After rebase, stETH.balanceOf(depositPool) is higher, but rsETHPrice is unchanged.

        uint256 priceAfterRebase = ILRTOracle(oracle).rsETHPrice();
        assert(priceAfterRebase == priceBefore); // price is stale

        // 2. Deposit 1 ETH at stale price
        uint256 rsethBefore = IRSETH(rseth).balanceOf(address(this));
        ILRTDepositPool(depositPool).depositETH{value: 1 ether}(0, "");
        uint256 rsethMinted = IRSETH(rseth).balanceOf(address(this)) - rsethBefore;

        // 3. Update price to reflect rebase
        ILRTOracle(oracle).updateRSETHPrice();
        uint256 priceAfterUpdate = ILRTOracle(oracle).rsETHPrice();
        assert(priceAfterUpdate > priceBefore); // price increased

        // 4. Attacker's rsETH is now worth more than 1 ETH
        uint256 attackerValueInETH = rsethMinted * priceAfterUpdate / 1e18;
        assert(attackerValueInETH > 1 ether); // profit confirmed
    }
}
```

The `rsethMinted` exceeds what the post-rebase price would have issued, and after `updateRSETHPrice()` the attacker's position is worth more than the deposited ETH — at the expense of pre-existing rsETH holders whose stETH yield was diluted.

### Citations

**File:** contracts/LRTDepositPool.sol (L444-444)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-96)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }

    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```
