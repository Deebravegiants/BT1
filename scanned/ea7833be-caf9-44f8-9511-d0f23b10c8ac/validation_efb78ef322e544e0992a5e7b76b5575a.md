I have the full contract. Let me verify the exact arithmetic and check whether `wrsETH.mint` accepts a zero amount without reverting.

### Title
Zero-rsETHAmount Deposit Silently Consumes Depositor ETH — (`contracts/pools/RSETHPoolV2NBA.sol`)

---

### Summary

`RSETHPoolV2NBA.deposit` accepts any non-zero ETH value but contains no guard requiring the computed `rsETHAmount` to be greater than zero. When a deposit is small enough that integer division in `viewSwapRsETHAmountAndFee` rounds `rsETHAmount` to zero, the transaction succeeds, the ETH is retained in the pool, and the depositor receives nothing.

---

### Finding Description

The `deposit` function in `RSETHPoolV2NBA` only validates that `msg.value != 0`: [1](#0-0) 

It then calls `viewSwapRsETHAmountAndFee`, which computes: [2](#0-1) 

Both divisions truncate toward zero. For any deposit where `amountAfterFee * 1e18 < rsETHToETHrate`, `rsETHAmount` evaluates to `0`. Since rsETH always accrues yield, `rsETHToETHrate` is always `> 1e18`, meaning a deposit of exactly 1 wei always produces `rsETHAmount = 0`.

The `wrsETH` token's `mint` implementation delegates directly to OpenZeppelin's `_mint`: [3](#0-2) 

OpenZeppelin's `_mint` does **not** revert on `amount = 0` — it emits a `Transfer(address(0), to, 0)` event and returns normally. The call at line 115 therefore succeeds silently, minting nothing.

The deposited ETH lands in `address(this).balance`. Because `fee` also rounds to 0 for tiny amounts, `feeEarnedInETH` is not incremented, so the ETH is included in the bridgeable balance: [4](#0-3) 

When `moveAssetsForBridging` is called by the BRIDGER_ROLE, this ETH is swept to the bridger. The depositor has no claim to it and no mechanism to recover it.

---

### Impact Explanation

A depositor who sends a sub-threshold ETH amount (e.g., 1 wei, or any amount where `amountAfterFee * 1e18 < rsETHToETHrate`) loses their ETH permanently with no wrsETH issued and no revert. The ETH is temporarily frozen in the pool until the next bridging call, at which point it is swept to L1 and irrecoverable by the depositor. This matches the **Medium — Temporary freezing of funds** scope.

---

### Likelihood Explanation

- No special role or permission is required; `deposit` is a public payable function.
- Any user sending a small ETH amount (including automated scripts, bots, or users testing with dust amounts) can trigger this.
- The threshold is low but non-trivial: with a typical rate of ~1.05e18, any deposit of 1 wei triggers the bug. The minimum safe deposit is `ceil(rsETHToETHrate / 1e18)` wei of `amountAfterFee`.
- No front-running or external dependency is needed.

---

### Recommendation

Add a post-computation guard in `deposit` that reverts if `rsETHAmount == 0`:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
if (rsETHAmount == 0) revert InvalidAmount();
```

Alternatively, enforce a minimum deposit amount at the entry point based on the current rate.

---

### Proof of Concept

```solidity
// Preconditions:
//   feeBps = 100 (1%)
//   rsETHToETHrate = 1.05e18 (oracle returns 1.05 ETH per rsETH)
//   depositor calls deposit{value: 1}("")

// Step 1: amount = 1 wei, passes `amount == 0` check
// Step 2: viewSwapRsETHAmountAndFee(1)
//   fee = 1 * 100 / 10_000 = 0
//   amountAfterFee = 1 - 0 = 1
//   rsETHAmount = 1 * 1e18 / 1.05e18 = 0  ← truncated to zero
// Step 3: feeEarnedInETH += 0
// Step 4: wrsETH.mint(depositor, 0)  ← no-op, does not revert
// Step 5: 1 wei is now in address(this).balance, depositor has 0 wrsETH
// Step 6: next moveAssetsForBridging() call sweeps the 1 wei to L1
//         depositor has no recourse

// Fuzz assertion: for all amount in [1, rsETHToETHrate/1e18],
//   either rsETHAmount > 0 OR tx reverts — currently NEITHER holds.
```

### Citations

**File:** contracts/pools/RSETHPoolV2NBA.sol (L106-118)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L124-133)
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

**File:** contracts/pools/RSETHPoolV2NBA.sol (L151-158)
```text
    function moveAssetsForBridging() external nonReentrant onlyRole(BRIDGER_ROLE) {
        // withdraw ETH - fees
        uint256 ethBalanceMinusFees = address(this).balance - feeEarnedInETH;

        (bool success,) = msg.sender.call{ value: ethBalanceMinusFees }("");
        if (!success) revert TransferFailed();

        emit AssetsMovedForBridging(ethBalanceMinusFees);
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L190-192)
```text
    function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
        _mint(_to, _amount);
    }
```
