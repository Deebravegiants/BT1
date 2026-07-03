### Title
Fee-Less Deposits via Integer Division Truncation in `viewSwapRsETHAmountAndFee` - (File: contracts/pools/RSETHPoolV3.sol)

---

### Summary

All L2 pool contracts compute the protocol deposit fee as `fee = amount * feeBps / 10_000`. Because Solidity integer division truncates toward zero, any deposit whose `amount * feeBps` product is less than `10_000` yields `fee = 0`. No guard prevents the deposit from proceeding with a zero fee, so a depositor can receive rsETH/wrsETH without paying the intended protocol fee.

---

### Finding Description

Every pool variant computes the fee identically inside `viewSwapRsETHAmountAndFee`:

```solidity
// RSETHPoolV3.sol – line 300
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;   // equals amount when fee == 0
``` [1](#0-0) 

The same pattern is replicated verbatim in `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`, `RSETHPool.sol`, `RSETHPoolNoWrapper.sol`, `RSETHPoolV2.sol`, `RSETHPoolV2ExternalBridge.sol`, and `RSETHPoolV2NBA.sol`. [2](#0-1) [3](#0-2) 

The deposit entry points only reject `amount == 0`; they do not check whether the computed fee is zero:

```solidity
// RSETHPoolV3.sol – deposit(string)
if (amount == 0) revert InvalidAmount();

(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
feeEarnedInETH += fee;          // silently adds 0
wrsETH.mint(msg.sender, rsETHAmount);
``` [4](#0-3) 

---

### Impact Explanation

**Low – Contract fails to deliver promised returns, but doesn't lose value.**

The protocol is designed to collect a basis-point fee on every deposit. When `fee` truncates to zero the protocol treasury receives nothing for that deposit, while the depositor receives the full rsETH/wrsETH equivalent of their input. Fee revenue is permanently lost for every qualifying deposit; no user funds are at risk.

---

### Likelihood Explanation

**Low.** The truncation threshold is `amount < 10_000 / feeBps`. For a typical `feeBps = 5` (0.05 %) this is `amount < 2 000 wei` of ETH — roughly $0.000000005 at current prices. The gas cost of any L2 transaction dwarfs the fee savings, making deliberate exploitation economically irrational. The issue is nonetheless a real code defect: the contract silently accepts fee-free deposits rather than reverting, contrary to the stated fee model.

---

### Recommendation

Add a post-computation guard in `viewSwapRsETHAmountAndFee` (or in each `deposit` function) that reverts when the calculated fee is zero but `feeBps > 0`:

```solidity
fee = amount * feeBps / 10_000;
if (feeBps > 0 && fee == 0) revert FeeTooSmall();
```

This mirrors the fix applied in the referenced Aave MR#75 and ensures every deposit that is subject to a fee actually pays one.

---

### Proof of Concept

1. Deploy `RSETHPoolV3` with `feeBps = 5`.
2. Call `deposit{value: 1999}("")` (1 999 wei of ETH).
3. Inside `viewSwapRsETHAmountAndFee`: `fee = 1999 * 5 / 10_000 = 9995 / 10_000 = 0` (integer truncation).
4. `feeEarnedInETH += 0`; `wrsETH.mint(msg.sender, rsETHAmount)` executes with the full 1 999 wei treated as `amountAfterFee`.
5. The depositor receives rsETH equivalent to 1 999 wei with zero fee deducted; the treasury receives nothing. [5](#0-4)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L256-264)
```text
        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L418-421)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

```

**File:** contracts/pools/RSETHPool.sol (L335-337)
```text
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
        uint256 amountAfterFee = amount - fee;
```
