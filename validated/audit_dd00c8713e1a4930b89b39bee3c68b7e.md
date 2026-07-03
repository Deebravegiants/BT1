### Title
`depositAsset` Mints rsETH Based on Stated `depositAmount` Rather Than Actual Received Balance — (`contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool.depositAsset` calculates the rsETH mint amount from the caller-supplied `depositAmount` parameter and then calls `safeTransferFrom` for that same value. For stETH — a supported, shares-based rebasing token — `safeTransferFrom` may credit 1–2 wei less than the requested amount due to integer rounding in Lido's internal shares arithmetic. The protocol mints rsETH against the stated `depositAmount` rather than the actual balance increase, creating a persistent, accumulating over-issuance of rsETH relative to real backing.

---

### Finding Description

`depositAsset` follows this sequence:

```
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount)   // uses depositAmount
IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount)
_mintRsETH(rsethAmountToMint)                                    // mints against depositAmount
``` [1](#0-0) 

`getRsETHAmountToMint` converts `depositAmount` directly to an rsETH quantity via the oracle price: [2](#0-1) 

No balance snapshot is taken before or after the `safeTransferFrom`. The actual tokens credited to the contract are never measured; only the user-supplied `depositAmount` is used.

stETH is a supported asset in this protocol (`LRTConstants.ST_ETH_TOKEN`, `stakeEthForStETH`, `UnstakeStETH` adapter in `LRTConverter`). [3](#0-2) 

stETH's `transferFrom` internally converts the requested token amount to a share count via integer division, then converts back. This round-trip can yield 1–2 wei less than the requested amount. The contract therefore holds `depositAmount − δ` stETH (where δ ∈ {1, 2}) but has minted rsETH as if it holds the full `depositAmount`.

The root cause is structurally identical to the referenced report: a stated/returned quantity is used for accounting instead of the actual post-transfer balance change.

---

### Impact Explanation

Every stETH deposit mints a fractionally larger rsETH amount than is backed by real assets. The discrepancy is 1–2 wei per call, but it accumulates monotonically with deposit volume. Over time the total rsETH supply exceeds the stETH backing, making the protocol technically insolvent by a small but non-zero margin. The last redeemers in a full-withdrawal scenario would receive slightly less than their proportional share.

**Impact: Low — Contract fails to deliver promised returns (persistent, accumulating under-collateralisation).**

---

### Likelihood Explanation

stETH is a core supported asset. Every ordinary user deposit of stETH triggers the path. No special conditions, attacker privileges, or external protocol compromise are required. The rounding shortfall is deterministic and occurs on virtually every stETH `transferFrom` call.

---

### Recommendation

Capture the contract's balance of `asset` before and after `safeTransferFrom`, and use the measured delta — not `depositAmount` — as the basis for both the rsETH mint calculation and any accounting:

```solidity
uint256 balanceBefore = IERC20(asset).balanceOf(address(this));
IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
uint256 actualReceived = IERC20(asset).balanceOf(address(this)) - balanceBefore;

uint256 rsethAmountToMint = getRsETHAmountToMint(asset, actualReceived);
if (rsethAmountToMint < minRSETHAmountExpected) revert MinimumAmountToReceiveNotMet();
_mintRsETH(rsethAmountToMint);
```

---

### Proof of Concept

1. Alice calls `depositAsset(stETH, 1e18, 0, "")`.
2. `getRsETHAmountToMint(stETH, 1e18)` returns `X` rsETH.
3. `safeTransferFrom` credits `1e18 − 1` stETH to the pool (stETH share rounding).
4. `_mintRsETH(X)` mints rsETH computed from `1e18`, not `1e18 − 1`.
5. The pool now backs `X` rsETH with `1e18 − 1` stETH — 1 wei short.
6. Repeated across millions of deposits, the cumulative shortfall grows proportionally, leaving the last withdrawers unable to redeem their full entitlement. [4](#0-3)

### Citations

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

**File:** contracts/LRTDepositPool.sol (L565-571)
```text
    function stakeEthForStETH(address referral, uint256 ethAmount) external onlyLRTManager {
        address stETHAddress = lrtConfig.getLSTToken(LRTConstants.ST_ETH_TOKEN);

        uint256 stETHShares = ILido(stETHAddress).submit{ value: ethAmount }(referral);

        emit AssetStaked(stETHAddress, ethAmount, stETHShares);
    }
```
