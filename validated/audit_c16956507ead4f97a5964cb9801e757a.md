Audit Report

## Title
`depositAsset` Mints rsETH Against Stated `depositAmount` Rather Than Actual Received Balance — (`contracts/LRTDepositPool.sol`)

## Summary

`LRTDepositPool.depositAsset` computes the rsETH mint amount from the caller-supplied `depositAmount` before executing `safeTransferFrom`, and mints against that pre-computed value without ever measuring the actual balance change. For stETH — a confirmed supported asset — `transferFrom` internally rounds share arithmetic, crediting 1–2 wei less than requested. The protocol therefore mints rsETH backed by `depositAmount − δ` stETH, creating a persistent, monotonically accumulating over-issuance.

## Finding Description

The execution path in `depositAsset` (lines 99–118) is:

```solidity
uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);
IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
_mintRsETH(rsethAmountToMint);
```

`_beforeDeposit` (lines 648–670) calls `getRsETHAmountToMint(asset, depositAmount)` (line 665), which computes:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

No balance snapshot is taken before or after `safeTransferFrom`. The actual tokens credited to the contract are never measured.

stETH is a confirmed supported asset (`LRTConstants.ST_ETH_TOKEN`, `stakeEthForStETH` at line 565, `UnstakeStETH` adapter, `LRTConverter` integration). stETH's `transferFrom` converts the requested token amount to an internal share count via integer division, then converts back — a round-trip that yields 1–2 wei less than the requested amount on virtually every call. The contract therefore holds `depositAmount − δ` stETH (δ ∈ {1, 2}) but has minted rsETH computed from the full `depositAmount`.

No existing guard catches this: `minRSETHAmountExpected` is checked against the pre-transfer calculation, not against a post-transfer recalculation, so it provides no protection.

## Impact Explanation

Every stETH deposit mints a fractionally larger rsETH amount than is backed by real assets. The discrepancy is 1–2 wei per call but accumulates monotonically with deposit volume. Over time the total rsETH supply exceeds the stETH backing, making the protocol technically under-collateralised by a small but non-zero and ever-growing margin. The last redeemers in a full-withdrawal scenario would receive slightly less than their proportional share.

**Impact: Low — Contract fails to deliver promised returns (persistent, accumulating under-collateralisation).**

## Likelihood Explanation

stETH is a core supported asset and the rounding shortfall is a deterministic property of Lido's share arithmetic. No special conditions, attacker privileges, or external protocol compromise are required. Every ordinary user deposit of stETH through the public `depositAsset` function triggers the path. The issue is self-executing and repeatable on every call.

## Recommendation

Capture the contract's balance of `asset` before and after `safeTransferFrom`, and use the measured delta as the basis for the rsETH mint calculation:

```solidity
uint256 balanceBefore = IERC20(asset).balanceOf(address(this));
IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
uint256 actualReceived = IERC20(asset).balanceOf(address(this)) - balanceBefore;

uint256 rsethAmountToMint = getRsETHAmountToMint(asset, actualReceived);
if (rsethAmountToMint < minRSETHAmountExpected) revert MinimumAmountToReceiveNotMet();
_mintRsETH(rsethAmountToMint);
```

This also requires moving the `minRSETHAmountExpected` check to after the transfer.

## Proof of Concept

1. Alice calls `depositAsset(stETH, 1e18, 0, "")`.
2. `_beforeDeposit` calls `getRsETHAmountToMint(stETH, 1e18)` → returns `X` rsETH (line 665).
3. `safeTransferFrom` credits `1e18 − 1` stETH to the pool due to stETH share rounding (line 114).
4. `_mintRsETH(X)` mints rsETH computed from `1e18`, not `1e18 − 1` (line 115).
5. The pool now backs `X` rsETH with `1e18 − 1` stETH — 1 wei short.
6. Repeated across N deposits, the cumulative shortfall grows to N×δ wei, leaving the last withdrawers unable to redeem their full entitlement.

**Foundry fork test plan:** Fork mainnet, deploy/use the existing `LRTDepositPool`, call `depositAsset` with real stETH, assert `IERC20(stETH).balanceOf(depositPool) == depositAmount` — this assertion will fail by 1–2 wei, confirming the discrepancy. An invariant test asserting `getTotalAssetDeposits(stETH) * rsETHPrice >= rsETH.totalSupply() * stETHPrice` will break after sufficient stETH deposits. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTDepositPool.sol (L110-115)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);
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

**File:** contracts/LRTDepositPool.sol (L648-670)
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
    }
```
