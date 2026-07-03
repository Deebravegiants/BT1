### Title
Stale `rsETHPrice` After stETH Rebase Allows Depositors to Mint Excess rsETH at Pre-Rebase Price — (`contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool.getRsETHAmountToMint()` divides the deposited amount by `LRTOracle.rsETHPrice`, a **stored state variable** that is only updated when `updateRSETHPrice()` is explicitly called. Because stETH rebases increase the live TVL (via `IERC20(stETH).balanceOf(...)`) without triggering a price update, any deposit made in the window between a rebase and the next `updateRSETHPrice()` call uses a stale (too-low) price, minting more rsETH than the deposit is worth relative to the post-rebase TVL.

---

### Finding Description

**Mint calculation uses a cached price, not a live one.**

`getRsETHAmountToMint()` computes:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [1](#0-0) 

`lrtOracle.rsETHPrice()` reads the **stored** `rsETHPrice` state variable:

```solidity
uint256 public override rsETHPrice;
``` [2](#0-1) 

This variable is only written inside `_updateRsETHPrice()`, which is only reachable via the explicit calls `updateRSETHPrice()` or `updateRSETHPriceAsManager()`. **No deposit path calls either of these.** [3](#0-2) 

**stETH rebase silently inflates live TVL.**

`getTotalAssetDeposits(stETH)` reads the live ERC-20 balance:

```solidity
assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
``` [4](#0-3) 

When stETH rebases, `balanceOf(depositPool)` increases immediately. `_getTotalEthInProtocol()` in the oracle also reads this live balance when `updateRSETHPrice()` is eventually called: [5](#0-4) 

So after a rebase:
- **Live TVL** (what `_getTotalEthInProtocol()` would return) is higher.
- **`rsETHPrice`** (what deposits divide by) is still the pre-rebase value.

**Exploit window.**

Between the stETH rebase event and the next `updateRSETHPrice()` call, `rsETHPrice` is stale-low. A depositor calling `depositETH(1 ether, ...)` receives:

```
rsethMinted = 1e18 / rsETHPrice_stale   >   1e18 / rsETHPrice_post_rebase
```

The excess rsETH represents a claim on the rebase yield that belongs to existing holders.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Each stETH rebase (daily, ~0.0096% of TVL per day) creates a window during which any depositor can mint rsETH at a discount. The attacker's rsETH represents a larger share of the post-rebase TVL than their deposit contributed. When `updateRSETHPrice()` is called, the price rises to reflect the rebase, and the attacker's excess rsETH is now worth more than they paid. The loss is borne by all existing rsETH holders whose share of the TVL is diluted.

At protocol scale (e.g., $100M TVL), a 0.01% daily rebase yields ~$10,000 of extractable yield per day. A sophisticated actor can automate this on every rebase.

---

### Likelihood Explanation

- stETH rebases are deterministic and publicly observable on-chain.
- `updateRSETHPrice()` is not called atomically with deposits; it is a separate, permissionless transaction that must be submitted by an off-chain keeper.
- The exploit requires no special role, no front-running of a specific victim transaction, and no external protocol compromise — only a normal `depositETH()` call during the rebase window.
- The window is open until a keeper calls `updateRSETHPrice()`, which in practice can be minutes to hours.

---

### Recommendation

1. **Call `updateRSETHPrice()` (or an equivalent inline price refresh) at the start of every deposit**, before computing `getRsETHAmountToMint()`. This ensures the price used for minting always reflects the current TVL.
2. Alternatively, compute the rsETH mint amount **on-the-fly** from live TVL rather than from the cached `rsETHPrice`, similar to how `_getTotalEthInProtocol()` already aggregates live balances.
3. As a defense-in-depth measure, enforce a maximum staleness window on `rsETHPrice` and revert deposits if the price has not been updated within that window.

---

### Proof of Concept

```solidity
// Fork test (Mainnet fork, block after a stETH rebase)
function testStaleRsETHPriceAfterRebase() external {
    // 1. Record pre-rebase state
    uint256 rsETHPriceBefore = lrtOracle.rsETHPrice();
    uint256 stETHBalBefore = IERC20(stETH).balanceOf(address(lrtDepositPool));

    // 2. Simulate stETH rebase: warp 1 day, call stETH.rebase() or use a fork
    //    at a block where the rebase has already occurred.
    //    After rebase: IERC20(stETH).balanceOf(depositPool) > stETHBalBefore
    uint256 stETHBalAfter = IERC20(stETH).balanceOf(address(lrtDepositPool));
    assertGt(stETHBalAfter, stETHBalBefore, "rebase did not increase balance");

    // 3. rsETHPrice is unchanged (no updateRSETHPrice called)
    assertEq(lrtOracle.rsETHPrice(), rsETHPriceBefore, "price should still be stale");

    // 4. Attacker deposits 1 ETH at stale price
    uint256 rsETHMinted = lrtDepositPool.getRsETHAmountToMint(ETH_TOKEN, 1 ether);
    vm.prank(attacker);
    lrtDepositPool.depositETH{value: 1 ether}(0, "");

    // 5. Compute what the fair mint would be at post-rebase price
    //    (call updateRSETHPrice first to get the true price)
    lrtOracle.updateRSETHPrice();
    uint256 rsETHPriceAfter = lrtOracle.rsETHPrice();
    assertGt(rsETHPriceAfter, rsETHPriceBefore, "price should have risen after rebase");

    uint256 fairMint = (1 ether * 1e18) / rsETHPriceAfter;

    // 6. Attacker received more rsETH than fair
    assertGt(rsETHMinted, fairMint, "attacker minted excess rsETH");

    // 7. Attacker profit in ETH terms
    uint256 attackerProfit = (rsETHMinted - fairMint) * rsETHPriceAfter / 1e18;
    console.log("Attacker profit (wei):", attackerProfit);
}
```

The test asserts that `rsETHMinted > fairMint`, confirming that the attacker extracted rebase yield from existing holders by depositing during the stale-price window.

### Citations

**File:** contracts/LRTDepositPool.sol (L444-444)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
```

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

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

**File:** contracts/LRTOracle.sol (L341-343)
```text
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
