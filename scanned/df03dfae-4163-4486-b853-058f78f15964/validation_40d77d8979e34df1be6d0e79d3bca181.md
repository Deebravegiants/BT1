Now I have all the information needed. Let me analyze the vulnerability carefully.

### Title
Missing Zero-Amount Guard in `deposit()` Allows ETH to Be Accepted While Minting 0 wrsETH — (`contracts/pools/RSETHPoolV2NBA.sol`)

---

### Summary

`RSETHPoolV2NBA.deposit()` accepts ETH and calls `wrsETH.mint(msg.sender, rsETHAmount)` without verifying that `rsETHAmount > 0`. Because `viewSwapRsETHAmountAndFee` uses integer division, small deposits produce `rsETHAmount = 0`. OpenZeppelin's `_mint` does not revert on a zero amount, so the transaction succeeds: the user's ETH is locked in the pool and 0 wrsETH is returned.

---

### Finding Description

In `viewSwapRsETHAmountAndFee`:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

This is integer division. When `amountAfterFee * 1e18 < rsETHToETHrate`, the result truncates to 0.

rsETH is a yield-bearing token whose rate starts at `1e18` and grows monotonically. Once any yield has accrued, `rsETHToETHrate > 1e18`. At that point, a deposit of 1 wei with `feeBps = 0` produces:

```
amountAfterFee = 1
rsETHAmount    = 1 * 1e18 / rsETHToETHrate = 0   (integer truncation)
```

`deposit()` then calls `wrsETH.mint(msg.sender, 0)`. The `mint` implementation in `RsETHTokenWrapper` is:

```solidity
function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
    _mint(_to, _amount);   // OZ _mint: does NOT revert on amount == 0
}
```

The call succeeds. The user's 1 wei is accepted into the pool, `feeEarnedInETH` is unchanged (fee = 0), and the ETH sits in `address(this).balance - feeEarnedInETH`. The user receives 0 wrsETH and has no function to reclaim their ETH.

**Critically, the sibling contracts already have this guard.** `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, and `RSETHPoolV2ExternalBridge` all contain `if (rsETHAmount == 0) revert InvalidAmount()` after computing the swap. `RSETHPoolV2NBA` and `RSETHPoolV2` are missing it. [1](#0-0) [2](#0-1) [3](#0-2) 

---

### Impact Explanation

A user who sends 1 wei (or any amount where `amountAfterFee * 1e18 < rsETHToETHrate`) to `deposit()` will:
- Have their ETH permanently accepted by the contract
- Receive 0 wrsETH
- Have no user-facing function to recover the ETH

The ETH is not permanently lost to the protocol — the `BRIDGER_ROLE` can drain it via `moveAssetsForBridging()` — but the depositor has no recovery path. This is **temporary freezing of user funds**. [4](#0-3) 

---

### Likelihood Explanation

The trigger condition (`rsETHToETHrate > 1e18`) is the **normal operating state** of rsETH after any yield accrual. No oracle manipulation or admin compromise is required. Any user who sends a dust deposit (1 wei) — whether by accident, by a buggy frontend, or by a griefing script — will hit this path. The condition is always satisfied in production.

The per-incident loss is small (dust), but the invariant violation is unconditional and the fix is a one-line guard already present in the V3 contracts.

---

### Recommendation

Add a zero-amount check after computing `rsETHAmount` in `deposit()`, consistent with the pattern already used in `RSETHPoolV3` and its siblings:

```solidity
function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

+   if (rsETHAmount == 0) revert InvalidAmount();   // guard against rounding to zero

    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
``` [1](#0-0) 

---

### Proof of Concept

```solidity
// Local fork test — no mainnet interaction required
// Preconditions:
//   rsETHToETHrate = 1.05e18  (5% yield accrued, normal production state)
//   feeBps = 0
//   Pool is unpaused, wrsETH minter role granted to pool

function testZeroMintOnDustDeposit() public {
    // rate > 1e18 → 1 wei deposit rounds to 0 wrsETH
    oracle.setRate(1.05e18);

    uint256 balanceBefore = wrsETH.balanceOf(alice);
    uint256 poolEthBefore = address(pool).balance;

    vm.prank(alice);
    pool.deposit{value: 1}("ref");   // 1 wei, succeeds with no revert

    // Invariant violated:
    assertEq(wrsETH.balanceOf(alice), balanceBefore);          // 0 wrsETH minted
    assertEq(address(pool).balance, poolEthBefore + 1);        // ETH accepted
    // Alice has no function to reclaim her 1 wei
}
``` [2](#0-1)

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

**File:** contracts/pools/RSETHPoolV2NBA.sol (L150-159)
```text
    /// @dev Legacy function - Withdraws assets from the contract for bridging
    function moveAssetsForBridging() external nonReentrant onlyRole(BRIDGER_ROLE) {
        // withdraw ETH - fees
        uint256 ethBalanceMinusFees = address(this).balance - feeEarnedInETH;

        (bool success,) = msg.sender.call{ value: ethBalanceMinusFees }("");
        if (!success) revert TransferFailed();

        emit AssetsMovedForBridging(ethBalanceMinusFees);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L190-192)
```text
    function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
        _mint(_to, _amount);
    }
```
