### Title
Stale `rsETHPrice` vs. Fresh `getAssetPrice` Mismatch in Deposit Minting Allows Over-Minting of rsETH at Existing Holders' Expense — (`contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool.getRsETHAmountToMint` computes the amount of rsETH to mint using a **fresh, live asset price** in the numerator and a **stale, stored rsETH price** in the denominator. Because the stored `rsETHPrice` is only updated when `LRTOracle._updateRsETHPrice()` is explicitly called, any period of rising asset prices creates a window where depositors receive more rsETH than they are entitled to, directly diluting existing rsETH holders.

---

### Finding Description

`LRTDepositPool.getRsETHAmountToMint` (line 520) computes:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [1](#0-0) 

**Side 1 — Fresh asset price (numerator):**
`lrtOracle.getAssetPrice(asset)` is a live, view-only call that delegates to an external `IPriceFetcher` and returns the current market price at the moment of the transaction. [2](#0-1) 

**Side 2 — Stale rsETH price (denominator):**
`lrtOracle.rsETHPrice()` reads the public state variable `rsETHPrice`, which is only written inside `_updateRsETHPrice()`. This function must be called explicitly (via `updateRSETHPrice()` or `updateRSETHPriceAsManager()`); it is never called atomically with a deposit. [3](#0-2) [4](#0-3) [5](#0-4) 

**The mismatch:**
The true rsETH price is `totalETHInProtocol / rsethSupply`, where `totalETHInProtocol` is itself computed using `getAssetPrice()` for every supported asset. When any supported asset's price rises after the last oracle update:

- The stored `rsETHPrice` is **lower** than the true current price (it was computed with the old, lower asset prices).
- The fresh `getAssetPrice(asset)` in the numerator is **higher** (current market).

The minting formula therefore becomes:

```
rsethAmountToMint = (amount × freshHigherAssetPrice) / staleOldLowerRsETHPrice
                  > (amount × freshHigherAssetPrice) / trueCurrentRsETHPrice
```

The depositor receives more rsETH than their deposit is worth at the true current exchange rate.

The same structural mismatch exists symmetrically in `LRTWithdrawalManager.getExpectedAssetAmount` (line 593), where a stale `rsETHPrice` and a fresh `getAssetPrice` are used in the opposite ratio, allowing withdrawers to extract excess assets when asset prices fall before an oracle update. [6](#0-5) 

---

### Impact Explanation

**High — Theft of unclaimed yield / share value from existing rsETH holders.**

Every rsETH minted in excess of the true exchange rate dilutes the proportional claim of all existing holders. The "stolen" value is the accrued appreciation of the underlying assets (stETH, ETHx, etc.) since the last oracle update. In a rising-price environment — the normal condition for liquid staking tokens — this mismatch is continuously present between oracle updates. A large deposit timed to coincide with a period of stale oracle data extracts real ETH-denominated value from all current rsETH holders.

---

### Likelihood Explanation

**Medium-High.** The oracle update (`updateRSETHPrice`) is not called atomically with deposits. It is a separate, permissionless public function that relies on off-chain keepers or manual calls. LST prices (stETH, ETHx) accrue value continuously with each Ethereum epoch, so the stale-price window is always open to some degree. No special privileges, flash loans, or governance access are required — any ordinary depositor calling `depositAsset()` or `depositETH()` benefits from the mismatch whenever asset prices have risen since the last oracle update. [7](#0-6) [8](#0-7) 

---

### Recommendation

Call `lrtOracle.updateRSETHPrice()` at the beginning of `depositAsset()` and `depositETH()` (before `_beforeDeposit` is invoked), so that both the asset price and the rsETH price are computed from the same state. Alternatively, compute the rsETH mint amount using a live, view-only rsETH price derived from `_getTotalEthInProtocol() / rsethSupply` rather than the stored `rsETHPrice` state variable.

---

### Proof of Concept

**Setup:**
- Protocol holds 100 stETH (each worth 1.00 ETH) and 100 ETHx (each worth 1.00 ETH).
- Total TVL = 200 ETH, rsETH supply = 200, stored `rsETHPrice` = 1.00 ETH.

**Price movement (no oracle update yet):**
- stETH appreciates to 1.05 ETH per token (normal LST yield accrual over several days).
- True rsETH price = (100 × 1.05 + 100 × 1.00) / 200 = 205 / 200 = **1.025 ETH**.
- Stored `rsETHPrice` = **1.00 ETH** (stale).

**Attacker deposits 10 stETH without calling `updateRSETHPrice()` first:**

```
rsethAmountToMint = (10 × 1.05e18) / 1.00e18 = 10.5 rsETH   ← actual minted
true entitlement  = (10 × 1.05e18) / 1.025e18 ≈ 10.244 rsETH
over-minted       ≈ 0.256 rsETH  (≈ 2.5% excess)
```

The 0.256 rsETH excess represents ~0.262 ETH of value extracted from existing holders. At scale (e.g., a 1,000 stETH deposit), the over-minting is ~25.6 rsETH ≈ 26.2 ETH of dilution imposed on all current rsETH holders.

The attacker can repeat this every time asset prices rise before the oracle is updated, which is a continuous condition for yield-bearing LSTs.

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
