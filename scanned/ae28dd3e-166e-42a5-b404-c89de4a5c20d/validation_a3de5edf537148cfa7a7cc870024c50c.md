### Title
First Depositor Can Inflate rsETH Price via Donation to Freeze Subsequent Depositors' Funds - (File: contracts/LRTOracle.sol / contracts/LRTDepositPool.sol)

### Summary

The `LRTOracle` stores `rsETHPrice` as a cached value updated via the publicly callable `updateRSETHPrice()`. Because `getTotalAssetDeposits` counts raw `balanceOf` the deposit pool (including unsolicited donations), and because `pricePercentageLimit` defaults to `0` (disabling the price-increase guard), a first depositor can donate assets to inflate the stored price. After the price is committed, any subsequent depositor who passes `minRSETHAmountExpected = 0` will receive 0 rsETH while permanently losing their deposited assets.

### Finding Description

**Step 1 — Price is stored, not computed on-the-fly, but is publicly updatable.**

`getRsETHAmountToMint` divides by the stored `lrtOracle.rsETHPrice()`: [1](#0-0) 

`updateRSETHPrice()` is unrestricted and callable by anyone: [2](#0-1) 

**Step 2 — TVL calculation uses raw `balanceOf`, so donations inflate it.**

For LST assets, `assetLyingInDepositPool` is `IERC20(asset).balanceOf(address(this))`: [3](#0-2) 

For ETH, `ethLyingInDepositPool` is `address(this).balance`, and the contract has an open `receive()`: [4](#0-3) [5](#0-4) 

**Step 3 — The price-increase guard is disabled by default.**

`pricePercentageLimit` is a `uint256` that defaults to `0`. The guard condition short-circuits when it is `0`: [6](#0-5) 

With `pricePercentageLimit == 0`, `isPriceIncreaseOffLimit` is always `false`, so any arbitrarily large price increase is accepted by `updateRSETHPrice()`.

**Step 4 — `_beforeDeposit` does not enforce `rsethAmountToMint > 0`.**

The only guard is `rsethAmountToMint < minRSETHAmountExpected`. When a caller passes `minRSETHAmountExpected = 0`, the condition `0 < 0` is `false`, so execution continues and `_mintRsETH(0)` is called — minting nothing for the victim: [7](#0-6) [8](#0-7) 

### Impact Explanation

A victim who deposits assets and receives 0 rsETH has permanently lost those assets: they hold no rsETH to redeem, and there is no refund path. This is **direct theft / permanent freezing of deposited funds** — Critical severity.

### Likelihood Explanation

- `updateRSETHPrice()` is publicly callable with no access control.
- `pricePercentageLimit` is `0` by default (storage default), so the guard is off unless an admin explicitly sets it.
- The `receive()` fallback and `balanceOf`-based accounting make the donation trivially executable.
- Any user who calls `depositETH(0, "")` or `depositAsset(asset, amount, 0, "")` — a natural call pattern when no slippage protection is desired — is vulnerable.

### Recommendation

1. **Enforce `rsethAmountToMint > 0` unconditionally** in `_beforeDeposit`:
   ```solidity
   if (rsethAmountToMint == 0) revert ZeroRsETHMinted();
   ```
2. **Set a non-zero default for `pricePercentageLimit`** in `initialize`, or require it to be set before the first deposit is accepted.
3. **Pre-mint a meaningful amount of rsETH** to the protocol treasury at initialization to make the first-depositor attack economically infeasible.

### Proof of Concept

Assume `pricePercentageLimit == 0` (default) and ETH is a supported asset.

1. **Alice** calls `depositETH{value: 1 wei}(0, "")` → receives 1 wei rsETH. `rsETHPrice` is still `1 ether` (set when supply was 0).
2. Alice sends 10 000 ETH directly to `LRTDepositPool` (accepted by `receive()`).
3. Alice calls `LRTOracle.updateRSETHPrice()`. Inside `_updateRsETHPrice`:
   - `totalETHInProtocol = (10_000e18 + 1)` (donation + deposit)
   - `rsethSupply = 1`
   - `newRsETHPrice = (10_000e18 + 1) / 1 ≈ 10_001e18`
   - `pricePercentageLimit == 0` → guard skipped → `rsETHPrice` is committed as `≈10_001e18`.
4. **Bob** calls `depositETH{value: 10_000e18}(0, "")`:
   - `getRsETHAmountToMint` → `(10_000e18 * 1e18) / 10_001e18 = 0`
   - `_beforeDeposit`: `0 < 0` is false → no revert
   - `_mintRsETH(0)` → Bob receives 0 rsETH, 10 000 ETH is lost.
5. Alice calls `updateRSETHPrice()` again; her 1 wei rsETH now backs `≈20_001 ETH` of TVL. She can redeem via withdrawal for the full pool. [9](#0-8) [10](#0-9) [11](#0-10)

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L444-444)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L648-669)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```

**File:** contracts/LRTDepositPool.sol (L686-690)
```text
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-222)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
```

**File:** contracts/LRTOracle.sol (L249-250)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```
