### Title
Fee Calculation Rounds Down Allowing Depositors to Pay Zero or Reduced Fees - (File: contracts/pools/RSETHPool.sol, RSETHPoolV3.sol, RSETHPoolNoWrapper.sol)

---

### Summary

All L2 pool contracts compute swap fees using integer division that rounds down: `fee = amount * feeBps / 10_000`. When `amount * feeBps < 10_000`, the fee truncates to zero. An unprivileged depositor can exploit this on low-gas L2 chains by making many small deposits, paying zero protocol fees while still receiving rsETH.

---

### Finding Description

Every pool contract's `viewSwapRsETHAmountAndFee` function computes the fee as:

```solidity
fee = amount * feeBps / 10_000;
```

This is the ETH path in `RSETHPool.sol`: [1](#0-0) 

The token path in `RSETHPool.sol`: [2](#0-1) 

The same pattern in `RSETHPoolV3.sol`: [3](#0-2) 

And in `RSETHPoolNoWrapper.sol`: [4](#0-3) 

The `deposit()` function only guards against `amount == 0`: [5](#0-4) 

There is no minimum deposit amount enforced. Any `amount >= 1 wei` is accepted, and the computed `fee` is directly accumulated into `feeEarnedInETH` or `feeEarnedInToken[token]`: [6](#0-5) 

---

### Impact Explanation

**High — Theft of unclaimed yield (protocol fees).**

With `feeBps = 30` (0.3%), any deposit of `amount < 334 wei` of ETH produces `fee = 0`. The depositor receives rsETH proportional to the full `amount` (no fee deducted from `amountAfterFee`) while the protocol collects nothing. Repeated in a loop, an attacker can deposit arbitrarily large total ETH value in sub-threshold chunks, paying zero fees throughout. Even at non-zero but reduced fee amounts (e.g., `amount = 667 wei` → `fee = 1 wei` instead of the correct `2 wei`), each iteration saves 1 wei of fee, and the cumulative loss scales with loop count.

The fee revenue is the yield earned by the protocol from pool users. Systematic evasion constitutes direct theft of that unclaimed yield. [7](#0-6) 

---

### Likelihood Explanation

**High.** These pools are deployed on L2 chains (Base, Arbitrum, Optimism, etc.) where gas per transaction is a fraction of a cent. A single loop of thousands of sub-threshold deposits costs negligible gas while bypassing all fees. No special permissions, flash loans, or oracle manipulation are required — only a standard `deposit()` call with a small `msg.value`. The attack is permissionless and economically rational whenever gas cost per iteration is less than the fee saved per iteration. [8](#0-7) 

---

### Recommendation

Round the fee **up** instead of down. Replace:

```solidity
fee = amount * feeBps / 10_000;
```

with ceiling division:

```solidity
fee = (amount * feeBps + 9_999) / 10_000;
```

or use OpenZeppelin's `Math.mulDiv` with `Math.Rounding.Up`. Apply this fix to all four affected fee computation sites across `RSETHPool.sol`, `RSETHPoolV3.sol`, `RSETHPoolNoWrapper.sol`, `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`, and `AGETHPoolV3.sol`. [9](#0-8) [10](#0-9) 

---

### Proof of Concept

Assume `feeBps = 30` (0.3%), ETH price = $3,000, gas cost per L2 deposit ≈ $0.001.

1. Attacker calls `deposit("")` with `msg.value = 333 wei` (≈ $0.000001).
2. `fee = 333 * 30 / 10_000 = 9 / 10_000 = 0` (truncated).
3. `amountAfterFee = 333 - 0 = 333 wei` — full amount converted to rsETH, zero fee collected.
4. Repeat 10,000 times: total deposited = 3,330,000 wei ≈ $0.01, total fees stolen = 10,000 × 1 wei = 10,000 wei ≈ $0.00003, total gas ≈ $10.
5. At higher `feeBps` or with tokens of higher per-wei USD value (e.g., wstETH), the per-iteration fee saving increases, making the attack profitable at much lower loop counts. [11](#0-10)

### Citations

**File:** contracts/pools/RSETHPool.sol (L265-278)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPool.sol (L311-319)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPool.sol (L335-337)
```text
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
        uint256 amountAfterFee = amount - fee;
```

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

**File:** contracts/pools/RSETHPoolV3.sol (L299-301)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L277-279)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```
