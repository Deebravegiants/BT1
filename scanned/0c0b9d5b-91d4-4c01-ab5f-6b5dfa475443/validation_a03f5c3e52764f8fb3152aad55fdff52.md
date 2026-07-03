### Title
Pool Deposit Functions Allow Zero rsETH Minting When Deposit Amount Rounds to Zero - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The `deposit` functions across all pool contracts validate `amount > 0` but do not validate that the computed `rsETHAmount > 0`. Integer division in `viewSwapRsETHAmountAndFee` can produce `rsETHAmount = 0` for small deposits. The transaction succeeds, the user's ETH/tokens are retained by the pool, and the user receives zero rsETH/wrsETH — an exact analog to the AMM report's "addLiquidity with amount == 0" class.

### Finding Description
In `RSETHPoolV3.deposit(string)` and `deposit(address, uint256, string)`, the only input guard is:

```solidity
if (amount == 0) revert InvalidAmount();
``` [1](#0-0) 

The computed output is never validated. `viewSwapRsETHAmountAndFee` computes:

```solidity
fee = amount * feeBps / 10_000;
amountAfterFee = amount - fee;
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [2](#0-1) 

When `amountAfterFee * 1e18 < rsETHToETHrate`, integer division truncates `rsETHAmount` to `0`. For example, with `feeBps = 0` and `rsETHToETHrate = 1.1e18` (a realistic post-accrual rate), depositing `1 wei` yields:

```
rsETHAmount = 1 * 1e18 / 1.1e18 = 0
```

The deposit then proceeds to:

```solidity
wrsETH.mint(msg.sender, rsETHAmount);  // mints 0 tokens
``` [3](#0-2) 

The deposited ETH is retained in the pool (credited to `feeEarnedInETH` or the bridgeable balance), and the user receives nothing. The same pattern exists in the token deposit path: [4](#0-3) 

And is replicated identically across all pool variants:
- `contracts/pools/RSETHPoolV3ExternalBridge.sol`
- `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`
- `contracts/pools/RSETHPoolV2.sol`
- `contracts/pools/RSETHPoolV2ExternalBridge.sol`
- `contracts/pools/RSETHPoolNoWrapper.sol`
- `contracts/pools/RSETHPool.sol`
- `contracts/agETH/AGETHPoolV3.sol` [5](#0-4) [6](#0-5) 

### Impact Explanation
A depositor calling `deposit` with a non-zero but sub-threshold amount (e.g., 1 wei of ETH) has their funds accepted and retained by the pool contract, but receives 0 rsETH/wrsETH in return. The user has no claim on the deposited funds and cannot recover them — the ETH is pooled with the bridgeable balance and will be swept to L1 by the BRIDGER_ROLE. The user permanently loses their deposited amount with no recourse.

**Impact: Low — Contract fails to deliver promised returns.**

### Likelihood Explanation
Low. The threshold is extremely small (sub-wei-equivalent for ETH; slightly larger for tokens with lower oracle rates). A normal user would not intentionally deposit 1 wei. However, it can be triggered by:
- A contract integration that does not validate the output amount before calling `deposit`
- An automated script depositing dust amounts
- A griefing actor deliberately burning tiny amounts to pollute pool accounting

### Recommendation
Add a post-computation check in each `deposit` function to revert if the computed output amount is zero:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
if (rsETHAmount == 0) revert InvalidAmount();
```

This mirrors the fix applied in the referenced AMM report (checking `amount > 0`) but applied to the output side, which is the actual invariant that must hold.

### Proof of Concept
1. Deploy `RSETHPoolV3` with `feeBps = 0` and an oracle returning `rsETHToETHrate = 1.1e18`.
2. Call `deposit("")` with `msg.value = 1 wei`.
3. `viewSwapRsETHAmountAndFee(1)` returns `(rsETHAmount=0, fee=0)`.
4. `wrsETH.mint(msg.sender, 0)` executes — user receives 0 wrsETH.
5. The 1 wei of ETH remains in the pool, accessible only to the BRIDGER_ROLE.
6. User has permanently lost 1 wei with no on-chain recourse. [7](#0-6) [2](#0-1)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L246-265)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
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

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L373-384)
```text
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L115-128)
```text
    function deposit(string memory referralId) external payable nonReentrant {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        agETH.mint(msg.sender, agETHAmount);

        emit SwapOccurred(msg.sender, agETHAmount, fee, referralId);
    }
```
