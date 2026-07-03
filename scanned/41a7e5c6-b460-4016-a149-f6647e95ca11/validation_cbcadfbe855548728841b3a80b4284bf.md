### Title
Fee-on-Transfer Token Deposit Mints Excess wrsETH Due to Nominal Amount Used in Calculation - (`contracts/pools/RSETHPoolV3.sol`)

### Summary
All L2 pool `deposit(address token, uint256 amount, ...)` functions pass the caller-supplied `amount` directly into `viewSwapRsETHAmountAndFee(amount, token)` to determine how many wrsETH/rsETH tokens to mint, without first measuring the actual balance change from the `safeTransferFrom`. If a fee-on-transfer ERC-20 is ever added as a supported token, the contract will mint wrsETH proportional to the nominal `amount` while only holding `amount - transferFee` of the underlying asset, permanently over-issuing wrsETH and diluting all existing holders.

### Finding Description

Every token-deposit path in the L2 pool family follows the same three-step pattern:

```
IERC20(token).safeTransferFrom(msg.sender, address(this), amount);   // (1)
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token); // (2)
wrsETH.mint(msg.sender, rsETHAmount);                                 // (3)
```

Step (1) transfers `amount` tokens from the caller. For a fee-on-transfer token the contract actually receives `amount - transferFee`. Step (2) computes the wrsETH to mint using the **nominal** `amount`, not the actual balance delta. Step (3) mints the inflated quantity.

The same flaw is present in every pool variant:

| File | Lines |
|---|---|
| `contracts/pools/RSETHPoolV3.sol` | 284–290 |
| `contracts/pools/RSETHPoolV3ExternalBridge.sol` | 403–409 |
| `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol` | 320–326 |
| `contracts/pools/RSETHPoolNoWrapper.sol` | 262–268 |
| `contracts/pools/RSETHPool.sol` | 296–302 |
| `contracts/agETH/AGETHPoolV3.sol` | 145–151 |

This is structurally identical to the CSXTrade bug: in that report `depositedValue` (the actual received amount, reduced by a discount) was used in `getNetValue()` instead of the full `weiPrice`, causing a mis-accounting between what was received and what was distributed. Here, `amount` (the nominal requested amount) is used in `viewSwapRsETHAmountAndFee()` instead of the actual received amount, causing a mis-accounting between what was received and what is minted.

### Impact Explanation

Every deposit with a fee-on-transfer token mints `rsETHAmount` wrsETH calculated on `amount`, while the pool only holds `amount - transferFee` of the underlying. The pool's backing assets are therefore worth less than the outstanding wrsETH supply implies. This is protocol insolvency: existing wrsETH holders are diluted by the phantom value injected on each such deposit. The shortfall compounds with every deposit and is permanent — there is no mechanism to claw back the over-minted tokens.

**Impact: Protocol insolvency / permanent dilution of existing wrsETH holders.**

### Likelihood Explanation

The admin controls which tokens are added via `addSupportedToken`. Several real-world LSTs and stablecoins implement optional or conditional transfer fees (e.g., USDT's fee switch, rebasing tokens with fee-on-transfer modes). If any such token is added — even inadvertently — every subsequent depositor triggers the over-minting. No special attacker capability is required beyond calling the public `deposit` function with the affected token.

### Recommendation

Measure the actual balance change after `safeTransferFrom` and use that value for all downstream calculations:

```solidity
function deposit(address token, uint256 amount, string memory referralId) external ... {
    if (amount == 0) revert InvalidAmount();

    uint256 balanceBefore = IERC20(token).balanceOf(address(this));
    IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
    uint256 actualReceived = IERC20(token).balanceOf(address(this)) - balanceBefore;

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(actualReceived, token);

    feeEarnedInToken[token] += fee;
    wrsETH.mint(msg.sender, rsETHAmount);

    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
}
```

Apply the same fix to all pool variants listed above.

### Proof of Concept

1. Admin adds a fee-on-transfer token `FOT` (1% transfer fee) as a supported token in `RSETHPoolV3`.
2. Attacker calls `deposit(FOT, 1000e18, "")`.
3. `safeTransferFrom` moves 1000 FOT from attacker; contract receives 990 FOT (1% fee taken by token).
4. `viewSwapRsETHAmountAndFee(1000e18, FOT)` computes `rsETHAmount` based on 1000 FOT.
5. `wrsETH.mint(msg.sender, rsETHAmount)` mints wrsETH equivalent to 1000 FOT of value.
6. Pool holds only 990 FOT but has issued wrsETH backed by 1000 FOT — a 10 FOT shortfall per deposit.
7. Repeated deposits compound the insolvency; when existing holders redeem, the last redeemers cannot be made whole. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L284-290)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
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

**File:** contracts/pools/RSETHPool.sol (L296-302)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
```

**File:** contracts/agETH/AGETHPoolV3.sol (L145-151)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        agETH.mint(msg.sender, agETHAmount);
```
