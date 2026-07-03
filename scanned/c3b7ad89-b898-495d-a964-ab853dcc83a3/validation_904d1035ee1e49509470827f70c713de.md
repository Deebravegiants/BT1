### Title
Deposit with small amount of low-decimal token yields zero rsETH, permanently losing user funds — (`contracts/pools/RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolNoWrapper.sol`, `RSETHPool.sol`)

---

### Summary

All pool `deposit(token, amount, referralId)` functions compute `rsETHAmount` via integer division. For small deposits of low-decimal tokens the result truncates to zero. The contracts then transfer the user's tokens in, record zero fee, and mint/transfer zero rsETH out — with no revert and no refund. The deposited tokens are absorbed into the pool's collective balance and subsequently bridged to L1, permanently lost to the user.

---

### Finding Description

Every pool variant computes the output amount with the same formula:

```solidity
// RSETHPoolV3.sol  viewSwapRsETHAmountAndFee(amount, token)
fee = amount * feeBps / 10_000;          // can be 0
uint256 amountAfterFee = amount - fee;
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;  // can be 0
``` [1](#0-0) 

When `amountAfterFee * tokenToETHRate < rsETHToETHrate`, integer division yields `rsETHAmount = 0`. The deposit function then:

1. Pulls the user's tokens into the pool (`safeTransferFrom`).
2. Adds zero to `feeEarnedInToken[token]`.
3. Calls `wrsETH.mint(msg.sender, 0)` (or `rsETH.safeTransfer(msg.sender, 0)` in `RSETHPoolNoWrapper`). [2](#0-1) 

No guard checks whether `rsETHAmount == 0` before proceeding. The same pattern is present in all four pool variants: [3](#0-2) [4](#0-3) [5](#0-4) 

The deposited tokens are not tracked as belonging to any individual user; they sit in the pool's general balance and are swept to L1 by the next `bridgeTokens` / `moveAssetsForBridging` call, making recovery impossible.

---

### Impact Explanation

A user who deposits a small amount of a low-decimal token (e.g., USDC with 6 decimals, GUSD with 2 decimals) receives zero rsETH while their tokens are permanently transferred to the protocol's L1 vault. The user suffers a direct, unrecoverable loss of their deposited funds. Impact: **Low** (contract fails to deliver promised returns; the absolute value lost per transaction is small, but the loss is real and permanent).

---

### Likelihood Explanation

The pools explicitly support ERC-20 tokens with non-18 decimals (wstETH is 18, but the architecture allows any token with an oracle). For a token with 6 decimals (USDC) and a typical rsETH/ETH rate near 1.05e18, `rsETHAmount` rounds to zero whenever `amount < rsETHToETHrate / tokenToETHRate`. With `tokenToETHRate ≈ 3.33e14` (1 USDC unit ≈ 1/3000 ETH), the threshold is roughly 3 154 USDC units (≈ $0.003). Any deposit below that threshold silently burns the user's tokens. The likelihood is **Low** in normal usage but rises if a 2-decimal token (e.g., GUSD) is ever added, where the threshold reaches ~$0.30.

---

### Recommendation

Add a zero-output guard immediately after computing `rsETHAmount` in every `deposit` path:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
if (rsETHAmount == 0) revert InvalidAmount();
```

This mirrors the fix applied in the Velocimeter M-2 report: do not proceed with the operation when the computed output is zero.

---

### Proof of Concept

Assume `RSETHPoolV3` is deployed with a 6-decimal token (USDC) whose oracle reports `tokenToETHRate = 3.33e14` and `rsETHToETHrate = 1.05e18`, `feeBps = 0`.

```
amount = 3000  // 3000 USDC units = $0.003
rsETHAmount = 3000 * 3.33e14 / 1.05e18
            = 9.99e17 / 1.05e18
            = 0  (integer division truncates)
```

Calling `deposit(USDC, 3000, "")`:
- `safeTransferFrom(user, pool, 3000)` — 3000 USDC units leave the user.
- `wrsETH.mint(user, 0)` — user receives nothing.
- Transaction succeeds; user's 3000 USDC units are permanently absorbed into the pool.

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L282-293)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L324-334)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L401-411)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L260-270)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
```

**File:** contracts/pools/RSETHPool.sol (L294-305)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
```
