### Title
Fee Truncation to Zero via Integer Division Allows Fee-Free Deposits - (File: contracts/pools/RSETHPoolNoWrapper.sol)

---

### Summary

All L2 RSETHPool contracts compute the protocol fee using plain integer division: `fee = amount * feeBps / 10_000`. When `amount * feeBps < 10_000`, Solidity's integer division truncates the result to zero. A depositor can exploit this to make repeated small deposits and receive rsETH at the full rate while paying zero protocol fees, stealing the protocol's fee revenue.

---

### Finding Description

Every pool in the family computes the swap fee identically:

```solidity
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [1](#0-0) 

When `amount * feeBps < 10_000`, the division truncates to `fee = 0`. Then `amountAfterFee = amount` (the full deposit), and the user receives rsETH calculated on the full amount — no fee is deducted or accrued to `feeEarnedInETH`.

The same pattern is present in every pool variant: [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

The threshold below which fee truncates to zero is `floor(9_999 / feeBps)` wei. For example:

| `feeBps` | Fee rate | Max zero-fee deposit |
|---|---|---|
| 10 | 0.10% | 999 wei |
| 5 | 0.05% | 1 999 wei |
| 1 | 0.01% | 9 999 wei |

There is no minimum deposit check beyond `amount == 0`. [6](#0-5) 

---

### Impact Explanation

**High — Theft of unclaimed yield (protocol fees).**

The fee is the protocol's revenue stream. When it truncates to zero, the attacker receives rsETH at the full 1:1 ETH-equivalent rate while the protocol collects nothing. On L2 chains (Arbitrum, Optimism, Base, Unichain) where these pools are deployed, gas costs are negligible (sub-cent per transaction), making it economically rational to split any large deposit into many sub-threshold deposits and avoid all fees entirely. The attacker loses nothing beyond gas; the protocol loses all fee revenue on those deposits.

---

### Likelihood Explanation

**Medium.** The attack requires no special privileges — any caller of the public `deposit()` function can exploit it. The only cost is L2 gas, which is negligible. The attacker must know the current `feeBps` value (publicly readable) and compute the threshold. The attack is straightforward and repeatable. It is not self-limiting: the attacker can drain the entire fee revenue over time by batching many small deposits.

---

### Recommendation

Use ceiling division for the fee so that any non-zero deposit with a non-zero `feeBps` always yields at least 1 wei of fee:

```solidity
// Replace:
fee = amount * feeBps / 10_000;

// With (ceiling division):
fee = (amount * feeBps + 9_999) / 10_000;
```

Alternatively, add an explicit guard:

```solidity
fee = amount * feeBps / 10_000;
if (feeBps > 0 && fee == 0) revert InvalidAmount();
```

Apply the fix to all pool contracts: `RSETHPoolNoWrapper.sol`, `RSETHPool.sol`, `RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`, `RSETHPoolV2.sol`, `RSETHPoolV2ExternalBridge.sol`, `RSETHPoolV2NBA.sol`.

---

### Proof of Concept

Assume `feeBps = 10` (0.1% fee), rsETH/ETH rate = 1.05e18 (rsETH is worth 1.05 ETH).

**Normal deposit of 1 ETH (1e18 wei):**
- `fee = 1e18 * 10 / 10_000 = 1e15` (0.001 ETH)
- `amountAfterFee = 1e18 - 1e15 = 0.999e18`
- `rsETHAmount = 0.999e18 * 1e18 / 1.05e18 ≈ 0.951e18` rsETH
- Protocol earns: 1e15 wei

**Attacker splits into 1,001 deposits of 999 wei each (total ≈ 999,999 wei ≈ 0.001 ETH):**
- Per deposit: `fee = 999 * 10 / 10_000 = 0` (truncated)
- `amountAfterFee = 999`
- `rsETHAmount = 999 * 1e18 / 1.05e18 ≈ 951` rsETH per call
- Protocol earns: **0 wei** across all 1,001 calls

The attacker receives the same rsETH as a fee-paying depositor of equivalent total ETH, while the protocol collects zero fees. On L2 chains with ~$0.001 gas per tx, 1,001 transactions cost ~$1 in gas — trivially profitable for any deposit size above a few dollars. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-243)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L277-286)
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

**File:** contracts/pools/RSETHPool.sol (L312-313)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPoolV3.sol (L300-301)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L419-420)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L336-337)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```
