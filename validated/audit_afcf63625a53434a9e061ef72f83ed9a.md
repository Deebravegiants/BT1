### Title
User Receives Fewer rsETH Than Deposit Value Due to Rounding in `depositAsset()` - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.depositAsset()` transfers the full `depositAmount` from the user but mints rsETH calculated via integer division that rounds down. The rounding dust (the difference between the deposited value and the value of minted rsETH) is permanently retained by the protocol, accruing to existing rsETH holders at the depositor's expense.

### Finding Description
In `LRTDepositPool.depositAsset()`, the rsETH amount to mint is computed as:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

This is a floor division. The full `depositAmount` is then pulled from the user:

```solidity
IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
_mintRsETH(rsethAmountToMint);
```

Because `rsethAmountToMint` is rounded down, the ETH-equivalent value of the minted rsETH is strictly less than or equal to the ETH-equivalent value of `depositAmount`. The difference — up to `rsETHPrice / assetPrice` wei of the deposited asset per call — stays in the protocol and is never returned to the depositor. The same pattern applies to `depositETH()` and to `RSETHPoolV3.deposit()` (both ETH and token variants), where `rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate` also rounds down while the full input amount is consumed. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Impact Explanation
The depositor receives fewer rsETH than the fair value of their deposit. The shortfall is bounded by `rsETHPrice / assetPrice` wei of the deposited asset per transaction. With all supported assets using 18 decimals and prices near 1e18, the per-deposit loss is at most ~1–2 wei of the deposited asset, which is negligible in isolation. However, the structural invariant is broken: the protocol consistently takes slightly more than it gives, and the rounding residual permanently benefits existing rsETH holders rather than being returned to the depositor.

**Impact: Low** — Contract fails to deliver the exact promised returns; no depositor funds are stolen outright, but every deposit silently under-mints rsETH relative to the deposited value.

### Likelihood Explanation
This affects every call to `depositAsset()`, `depositETH()`, and `RSETHPoolV3.deposit()` by any unprivileged user. No special conditions are required; the rounding occurs unconditionally on every deposit. Likelihood is high (it always happens), but the per-transaction magnitude is negligible with 18-decimal tokens.

### Recommendation
Mirror the fix from the referenced report: after computing `rsethAmountToMint`, back-calculate the exact asset amount that corresponds to that many rsETH shares and transfer only that adjusted amount from the user, returning any remainder:

```solidity
// In depositAsset():
uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

// Back-calculate the exact deposit amount that maps to rsethAmountToMint
uint256 adjustedDepositAmount = (rsethAmountToMint * lrtOracle.rsETHPrice()) / lrtOracle.getAssetPrice(asset);

IERC20(asset).safeTransferFrom(msg.sender, address(this), adjustedDepositAmount);
_mintRsETH(rsethAmountToMint);
```

Apply the same adjustment in `depositETH()` (refund the ETH remainder via `msg.sender.call{value: msg.value - adjustedDepositAmount}("")`) and in `RSETHPoolV3.deposit()`.

### Proof of Concept
Assume:
- `assetPrice = 1e18` (stETH ≈ 1 ETH)
- `rsETHPrice = 1.1e18` (rsETH has accrued yield, worth 1.1 ETH)
- `depositAmount = 1.05e18` wei of stETH

Step 1 — `getRsETHAmountToMint` computes:
```
rsethAmountToMint = floor(1.05e18 * 1e18 / 1.1e18)
                  = floor(9.545...e17)
                  = 9.545e17  (truncated)
```

Step 2 — Full `1.05e18` wei of stETH is pulled from the user.

Step 3 — `9.545e17` rsETH is minted to the user.

Step 4 — Value of minted rsETH in stETH:
```
9.545e17 * 1.1e18 / 1e18 = 1.04995e18 wei of stETH
```

Step 5 — User loss: `1.05e18 - 1.04995e18 = 5e13` wei of stETH (~0.00005 stETH) per deposit. This residual is silently absorbed by the protocol. [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTDepositPool.sol (L110-115)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);
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

**File:** contracts/pools/RSETHPoolV3.sol (L282-292)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
```

**File:** contracts/pools/RSETHPoolV3.sol (L333-334)
```text
        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```
