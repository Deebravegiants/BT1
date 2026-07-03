### Title
Fee-on-Transfer Token Not Accounted for in `deposit` — Over-Minting of wrsETH/rsETH Leading to Pool Undercollateralization - (File: contracts/pools/RSETHPoolV3.sol)

---

### Summary

All L2 pool contracts (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolNoWrapper`) and the L1 `LRTDepositPool` compute the amount of wrsETH/rsETH to mint using the caller-supplied `amount` parameter rather than the actual token balance received after `safeTransferFrom`. If a supported ERC20 token charges a transfer fee, the pool receives fewer tokens than `amount` but mints wrsETH/rsETH as if the full `amount` arrived, permanently undercollateralizing the pool.

---

### Finding Description

In `RSETHPoolV3.deposit(address token, uint256 amount, string referralId)`: [1](#0-0) 

The contract calls `safeTransferFrom` for `amount`, then immediately passes the same `amount` to `viewSwapRsETHAmountAndFee` to compute `rsETHAmount` and `fee`. If the token deducts a transfer fee, the pool receives `amount * (1 - transferFee%)` but:

1. Mints `wrsETH` based on the full `amount` — over-minting by `amount * transferFee%` worth of wrsETH.
2. Increments `feeEarnedInToken[token]` based on the full `amount` — inflating the recorded fee. [2](#0-1) 

The same pattern is present verbatim in:
- `RSETHPoolV3ExternalBridge.deposit` [3](#0-2) 
- `RSETHPoolV3WithNativeChainBridge.deposit` [4](#0-3) 
- `RSETHPoolNoWrapper.deposit` [5](#0-4) 
- `LRTDepositPool.depositAsset` — `_beforeDeposit` computes `rsethAmountToMint` from `depositAmount` before the transfer occurs, then mints that amount regardless of what is actually received. [6](#0-5) 

A secondary consequence: `getTokenBalanceMinusFees` subtracts the inflated `feeEarnedInToken` from the real (lower) balance, causing the bridgeable balance to be understated and potentially causing `withdrawFees` to revert with an underflow if the fee accounting exceeds the actual balance. [7](#0-6) 

---

### Impact Explanation

Every deposit with a fee-on-transfer token mints more wrsETH than the token value actually held by the pool. The pool bridges fewer tokens to L1 than the wrsETH it has issued represents, making wrsETH permanently undercollateralized. Accumulated across many deposits, this constitutes protocol insolvency for the affected token. This maps to **Low — Contract fails to deliver promised returns** at minimum, escalating toward **Critical — Protocol insolvency** if the fee rate or deposit volume is significant.

---

### Likelihood Explanation

The protocol uses a `TIMELOCK_ROLE`-gated `addSupportedToken` to control which tokens are accepted. Currently deployed tokens (wstETH, ETH) do not have transfer fees. However, a token that is fee-free at listing time could activate fees later (e.g., governance vote), or an operator could mistakenly list a fee-on-transfer token. The external report's analog was classified Medium for the same reason. Likelihood is **Low** but non-zero given the protocol's multi-chain, multi-token expansion trajectory.

---

### Recommendation

Measure the actual received amount by comparing the pool's token balance before and after `safeTransferFrom`, and use that delta for all downstream calculations:

```solidity
uint256 balanceBefore = IERC20(token).balanceOf(address(this));
IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
uint256 actualReceived = IERC20(token).balanceOf(address(this)) - balanceBefore;

(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(actualReceived, token);
feeEarnedInToken[token] += fee;
wrsETH.mint(msg.sender, rsETHAmount);
```

Apply the same fix to `LRTDepositPool.depositAsset` by moving the `_beforeDeposit` rsETH calculation to after the transfer.

---

### Proof of Concept

1. Admin adds a token `T` with a 1% transfer fee as a supported token via `addSupportedToken`.
2. Attacker (or any depositor) calls `RSETHPoolV3.deposit(T, 1000e18, "")`.
3. Pool receives `990e18` of `T` (1% fee deducted by the token contract).
4. `viewSwapRsETHAmountAndFee(1000e18, T)` is called — computes `fee = 10e18`, `amountAfterFee = 990e18`, mints wrsETH for `990e18` worth.
5. `feeEarnedInToken[T] += 10e18` — but only `990e18` arrived, so the pool's actual balance is `990e18`.
6. `getTokenBalanceMinusFees(T)` = `990e18 - 10e18` = `980e18` — only `980e18` is available to bridge, but wrsETH representing `990e18` was minted.
7. Repeated deposits widen the gap; eventually the pool cannot cover all outstanding wrsETH redemptions, and `withdrawFees` may revert due to underflow when `feeEarnedInToken[T]` exceeds the actual balance. [1](#0-0) [6](#0-5)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L284-290)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolV3.sol (L371-373)
```text
    function getTokenBalanceMinusFees(address token) public view returns (uint256) {
        return IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L403-409)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L320-326)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L262-268)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);
```

**File:** contracts/LRTDepositPool.sol (L111-115)
```text
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);
```
