### Title
Donation-Inflated `rsETHPrice` via Public `updateRSETHPrice()` Causes Zero rsETH Minting for Depositors - (File: `contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`)

---

### Summary
The `LRTOracle.updateRSETHPrice()` function is public and permissionless. It computes `rsETHPrice` using live token balances of the deposit pool, which include any donated (non-deposited) tokens. An attacker can donate ETH or LST tokens directly to `LRTDepositPool`, then call `updateRSETHPrice()` to inflate the cached `rsETHPrice`. Because `getRsETHAmountToMint()` uses integer division against this inflated price, a victim depositor can receive zero rsETH for a real deposit, losing their funds to existing rsETH holders.

---

### Finding Description

**Step 1 — Donation inflates `totalETHInProtocol`.**

`LRTOracle._getTotalEthInProtocol()` calls `ILRTDepositPool.getTotalAssetDeposits(asset)` for every supported asset. [1](#0-0) 

`getTotalAssetDeposits()` for LST assets reads the live `balanceOf` of the deposit pool: [2](#0-1) 

For ETH it reads `address(this).balance`: [3](#0-2) 

The deposit pool accepts raw ETH via an unrestricted `receive()`: [4](#0-3) 

Any tokens or ETH sent directly to the contract are therefore immediately counted as protocol TVL.

**Step 2 — `updateRSETHPrice()` is public and permissionless.** [5](#0-4) 

Anyone can call it at any time to commit the inflated TVL into the stored `rsETHPrice`.

**Step 3 — `rsETHPrice` is computed as `totalETHInProtocol / rsethSupply`.** [6](#0-5) 

Donating tokens increases the numerator without increasing `rsethSupply`, so `rsETHPrice` rises.

**Step 4 — Minting uses integer division against the cached (now inflated) price.** [7](#0-6) 

If `rsETHPrice` has been inflated to `N × 1e18`, a victim depositing `M` ETH receives:

```
rsethAmountToMint = (M × 1e18) / (N × 1e18) = M / N
```

When `M < N`, this rounds down to **zero**. The victim's ETH is absorbed into the protocol and accrues to existing rsETH holders (including the attacker).

**Step 5 — Zero-mint is not blocked when `minRSETHAmountExpected = 0`.** [8](#0-7) 

If the victim passes `minRSETHAmountExpected = 0` (a valid and common default), the transaction succeeds and the victim receives nothing.

---

### Impact Explanation

A depositor loses their entire ETH or LST deposit and receives zero rsETH in return. The deposited value is redistributed to existing rsETH holders. This is direct theft of user funds at rest.

**Impact: Critical** — direct theft of deposited user funds.

---

### Likelihood Explanation

The attack requires the attacker to:
1. Hold a small amount of rsETH (or be the first depositor).
2. Donate an amount of ETH/LST at least equal to the victim's deposit.
3. Call the public `updateRSETHPrice()`.

The `pricePercentageLimit` guard partially mitigates this: if set to a non-zero value, a single large price jump reverts for non-managers. [9](#0-8) 

However:
- `pricePercentageLimit` is **not set in `initialize()`** — its default value is `0`, meaning the guard is disabled until an admin explicitly configures it.
- Even when set, the attacker can execute the inflation in multiple small increments (each within the allowed percentage), since `highestRsethPrice` is updated after each successful call.

**Likelihood: Low** — requires capital equal to the victim's deposit and depends on `pricePercentageLimit` being unset or bypassable via incremental updates.

---

### Recommendation

1. **Remove live `balanceOf` from TVL accounting.** Track deposited amounts in an internal accounting variable rather than reading `balanceOf(address(this))` or `address(this).balance`. Donated tokens should not affect `rsETHPrice`.

2. **Enforce a non-zero `pricePercentageLimit` at initialization.** Set a conservative default (e.g., 1%) in `initialize()` so the guard is active from deployment.

3. **Enforce a minimum rsETH output.** Revert in `_beforeDeposit` if `rsethAmountToMint == 0`, regardless of `minRSETHAmountExpected`.

4. **Restrict `updateRSETHPrice()`.** Consider making it callable only by a trusted keeper or the manager role, preventing an attacker from committing an inflated price on demand.

---

### Proof of Concept

```
Initial state:
  rsETHPrice = 1e18 (initial, rsethSupply == 0 → price reset to 1 ether)

Step 1: Attacker deposits 1 wei ETH via depositETH(0, "")
  rsethAmountToMint = (1 * 1e18) / 1e18 = 1 wei rsETH
  rsethSupply = 1 wei

Step 2: Attacker sends 1000 ETH directly to LRTDepositPool (via receive())
  address(this).balance in deposit pool = 1000 ETH + 1 wei

Step 3: Attacker calls LRTOracle.updateRSETHPrice()
  totalETHInProtocol = 1000 ETH + 1 wei  (includes donation)
  newRsETHPrice = (1000e18 + 1) / 1 ≈ 1000e18
  rsETHPrice is now ≈ 1000e18

Step 4: Victim calls depositETH(0, "") with msg.value = 500 ETH
  rsethAmountToMint = (500e18 * 1e18) / 1000e18 = 0  (rounds down)
  Victim receives 0 rsETH, 500 ETH is absorbed into the protocol

Step 5: Attacker (holding 1 wei rsETH out of total 1 wei supply) now owns
  the entire protocol TVL ≈ 1500 ETH, redeemable via withdrawal.
```

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
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

**File:** contracts/LRTDepositPool.sol (L667-669)
```text
        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
