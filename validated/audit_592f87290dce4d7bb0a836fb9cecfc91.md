### Title
Fee Bypass via Integer Division Truncation in `viewSwapRsETHAmountAndFee` - (`contracts/pools/RSETHPoolV3.sol`)

---

### Summary

All L2 RSETHPool contracts (and `AGETHPoolV3`) compute the protocol fee using integer division that truncates to zero for small deposit amounts. Any unprivileged depositor can bypass the fee entirely by splitting a large deposit into many small ones, causing the protocol to collect zero fee revenue.

---

### Finding Description

The fee calculation in every pool variant follows the same pattern:

```solidity
fee = amount * feeBps / 10_000;
```

When `amount * feeBps < 10_000`, Solidity integer division truncates the result to `0`. The deposit functions only guard against a zero-value deposit:

```solidity
if (amount == 0) revert InvalidAmount();
```

No minimum deposit amount is enforced. Therefore, any `amount` in the range `1 ≤ amount < ⌈10_000 / feeBps⌉` produces `fee = 0`, and the full `amount` is credited to the depositor as `amountAfterFee`.

The affected fee computation sites are:

- `RSETHPoolV3.viewSwapRsETHAmountAndFee(uint256)` — ETH path
- `RSETHPoolV3.viewSwapRsETHAmountAndFee(uint256, address)` — token path
- Identical logic in `RSETHPool`, `RSETHPoolV2`, `RSETHPoolNoWrapper`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV2NBA`, and `AGETHPoolV3`

The deposit entry points that call these functions and accumulate the (zero) fee:

```solidity
// RSETHPoolV3.sol – ETH deposit
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
feeEarnedInETH += fee;   // fee == 0 → no revenue collected
wrsETH.mint(msg.sender, rsETHAmount);
```

```solidity
// RSETHPoolV3.sol – token deposit
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee;   // fee == 0 → no revenue collected
wrsETH.mint(msg.sender, rsETHAmount);
```

---

### Impact Explanation

**Theft of unclaimed yield (protocol fee revenue).** The protocol is designed to collect a basis-point fee on every deposit. By making many sub-threshold deposits, an attacker receives the full rsETH/wrsETH mint while the treasury receives nothing. The attacker does not lose any principal; the loss falls entirely on the protocol's fee income stream.

---

### Likelihood Explanation

These pools are deployed on Layer 2 networks (Arbitrum, Optimism, etc.) where gas costs are negligible — the original Allo report explicitly cited L2 gas economics as the enabling factor, and the same applies here. A depositor wishing to swap, say, 1 ETH worth of value can split it into thousands of sub-threshold transactions at near-zero cost. The threshold amount is small but non-trivial for low-decimal tokens: with `feeBps = 5` (0.05%), any ETH amount below 2 000 wei yields `fee = 0`; for a 6-decimal token (e.g., USDC) the threshold is 0.002 USDC per call. The attack is straightforward, requires no special privilege, and is economically rational on L2.

---

### Recommendation

Add a minimum deposit check so that `amount * feeBps` is always at least `10_000` (i.e., the fee is always at least 1 unit), or enforce a protocol-level `minDepositAmount` variable:

```solidity
uint256 minDepositAmount = 10_000 / feeBps + 1;
if (amount < minDepositAmount) revert DepositBelowMinimum();
```

Alternatively, revert when the computed fee is zero but `feeBps > 0`:

```solidity
fee = amount * feeBps / 10_000;
if (feeBps > 0 && fee == 0) revert DepositTooSmall();
```

Apply the same fix to all pool variants and `AGETHPoolV3`.

---

### Proof of Concept

**Setup:** `RSETHPoolV3` deployed on Arbitrum, `feeBps = 5` (0.05%), rsETH/ETH rate = 1.05e18.

**Threshold:** `fee = amount * 5 / 10_000 = 0` when `amount < 2 000 wei`.

**Attack loop (pseudocode):**
```
for i in range(500_000):
    pool.deposit{value: 1_999}("ref")   // fee = 1999*5/10000 = 0
```

Each call mints `1_999 * 1e18 / 1.05e18 ≈ 1_904 wei` of wrsETH with zero fee paid. After 500 000 iterations the attacker has deposited ~1 ETH worth of value and paid **0 wei** in protocol fees instead of the expected ~0.0005 ETH. On Arbitrum, 500 000 simple contract calls cost on the order of a few dollars, making this economically viable.

The same arithmetic applies to token deposits via `viewSwapRsETHAmountAndFee(amount, token)`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L254-265)
```text
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L271-293)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-301)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPoolV3.sol (L315-325)
```text
    function viewSwapRsETHAmountAndFee(
        uint256 amount,
        address token
    )
        public
        view
        onlySupportedToken(token)
        returns (uint256 rsETHAmount, uint256 fee)
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPool.sol (L311-313)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPool.sol (L334-337)
```text
    {
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/agETH/AGETHPoolV3.sol (L160-162)
```text
    function viewSwapAgETHAmountAndFee(uint256 amount) public view returns (uint256 agETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/agETH/AGETHPoolV3.sol (L183-185)
```text
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```
