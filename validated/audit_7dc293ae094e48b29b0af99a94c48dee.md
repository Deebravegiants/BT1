### Title
Donation Attack on `LRTDepositPool` Inflates `rsETHPrice` via Raw `balanceOf()` Accounting, Causing Depositors to Receive Zero rsETH - (File: contracts/LRTDepositPool.sol, contracts/LRTOracle.sol)

---

### Summary

An unprivileged attacker can directly transfer assets (ETH or ERC20) to `LRTDepositPool` and then call the public `updateRSETHPrice()` function to inflate the stored `rsETHPrice`. Because `getRsETHAmountToMint()` divides by this stored price, subsequent depositors receive zero rsETH while permanently losing their deposited assets to the pool. This is the direct analog of the CToken empty-pool exchange-rate manipulation described in the report.

---

### Finding Description

**Root cause 1 — raw `balanceOf()` in TVL accounting:**

`LRTDepositPool.getAssetDistributionData()` computes the deposit pool's share of TVL using the contract's live token balance:

```solidity
assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
``` [1](#0-0) 

For ETH the same pattern applies:

```solidity
ethLyingInDepositPool = address(this).balance;
``` [2](#0-1) 

The contract also has an open `receive()` that accepts arbitrary ETH:

```solidity
receive() external payable { }
``` [3](#0-2) 

Any direct transfer of tokens or ETH to `LRTDepositPool` therefore inflates `getTotalAssetDeposits()` and, by extension, `totalETHInProtocol`.

**Root cause 2 — public `updateRSETHPrice()` with no price-increase guard when `pricePercentageLimit == 0`:**

`LRTOracle._updateRsETHPrice()` computes the new price as:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [4](#0-3) 

The only guard against an unbounded price increase is:

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
``` [5](#0-4) 

`pricePercentageLimit` is a plain `uint256` storage variable that defaults to **zero**. When it is zero the condition short-circuits to `false`, so no revert occurs regardless of how large the price jump is. The function is callable by anyone:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [6](#0-5) 

**Root cause 3 — minting uses the stale stored price:**

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [7](#0-6) 

`lrtOracle.rsETHPrice()` is the stored value last written by `updateRSETHPrice()`. If that value has been inflated by a donation attack, every subsequent depositor is divided by the inflated denominator.

---

### Impact Explanation

When `pricePercentageLimit == 0` (the Solidity default, set by no initializer), an attacker who holds even 1 wei of rsETH can:

1. Donate a large amount of a supported asset directly to `LRTDepositPool`.
2. Call `updateRSETHPrice()` to write the inflated price into storage.
3. Any victim who then calls `depositETH` or `depositAsset` receives `rsethAmountToMint = (amount × assetPrice) / inflatedPrice`, which rounds to **zero** in integer arithmetic.

The victim's deposited assets are permanently absorbed into the pool. The attacker's rsETH, being the only outstanding supply, represents a claim on the entire pool including the victim's funds. This is **direct theft of user funds** — Critical severity.

---

### Likelihood Explanation

- `pricePercentageLimit` is `0` by default and must be explicitly set by an admin after deployment. Any window where it is unset (including the initial deployment period) is exploitable.
- `updateRSETHPrice()` is callable by any EOA or contract with no role restriction.
- The `LRTDepositPool` `receive()` function and standard ERC-20 `transfer()` provide the donation vector with no access control.
- The only user-side protection is `minRSETHAmountExpected`, which many users set to `0` or which front-ends may compute before the attack transaction lands.
- The attack is front-runnable: the attacker observes a pending deposit, donates, updates the price, and the victim's transaction executes against the inflated price.

Likelihood: **Medium** (requires `pricePercentageLimit == 0`, which is the default state).

---

### Recommendation

1. **Replace raw `balanceOf()` with an internal accounting variable** (analogous to Compound's `internalCash`) that is only incremented through the official deposit path, making donations invisible to the price oracle.
2. **Require `pricePercentageLimit > 0` in the initializer** or enforce a hard-coded maximum price-increase cap per oracle update.
3. **Restrict `updateRSETHPrice()` to an authorized role** (e.g., `MANAGER` or a keeper) so that arbitrary callers cannot trigger a price update immediately after a donation.
4. **Enforce a non-zero `minRSETHAmountExpected`** at the protocol level to guarantee depositors always receive at least some rsETH.

---

### Proof of Concept

Assume `pricePercentageLimit == 0` (default), stETH price ≈ 1 ETH, and the protocol has just launched.

| Step | Action | rsETH supply | `totalETHInProtocol` | `rsETHPrice` (stored) |
|------|--------|-------------|----------------------|----------------------|
| 1 | Attacker deposits 1 wei stETH via `depositAsset` | 1 wei | 1 wei | 1e18 (1 ETH) |
| 2 | Attacker transfers 1 000 stETH directly to `LRTDepositPool` | 1 wei | 1 000 × 1e18 + 1 | 1e18 (stale) |
| 3 | Attacker calls `updateRSETHPrice()` | 1 wei | 1 000 × 1e18 + 1 | ≈ 1 000 × 1e36 |
| 4 | Victim calls `depositAsset(stETH, 1e18, 0, "")` | 1 wei | — | — |

At step 4, `getRsETHAmountToMint` computes:

```
rsethAmountToMint = (1e18 × 1e18) / (1 000 × 1e36)
                  = 1e36 / 1e39
                  = 0   ← integer truncation
``` [8](#0-7) 

The check `rsethAmountToMint < minRSETHAmountExpected` passes when `minRSETHAmountExpected == 0`, so the transaction succeeds. The victim's 1 stETH is transferred into `LRTDepositPool` and the victim receives **zero rsETH**. The attacker's 1 wei rsETH now represents a claim on ≈ 1 001 stETH. [9](#0-8) [10](#0-9) [11](#0-10)

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

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L218-222)
```text
        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
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
