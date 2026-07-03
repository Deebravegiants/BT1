Now I have the full picture. Let me analyze the vulnerability precisely.

### Title
Missing Zero-Amount Guard on `rsETHAmount` Allows ETH Deposits to Succeed While Minting 0 wrsETH — (`contracts/pools/RSETHPoolV2NBA.sol`)

---

### Summary

`RSETHPoolV2NBA.deposit()` accepts ETH and calls `wrsETH.mint(msg.sender, rsETHAmount)` without verifying that `rsETHAmount > 0`. Because `viewSwapRsETHAmountAndFee` uses integer division (`amountAfterFee * 1e18 / rsETHToETHrate`), any deposit small enough that `amountAfterFee * 1e18 < rsETHToETHrate` silently rounds `rsETHAmount` to zero. The ETH is accepted, no wrsETH is minted, and the user has no on-chain path to recover their funds.

---

### Finding Description

In `RSETHPoolV2NBA.sol`, the `deposit()` function:

```solidity
function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();                    // only guards zero ETH
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);                       // no guard: rsETHAmount may be 0
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
``` [1](#0-0) 

The amount calculation in `viewSwapRsETHAmountAndFee`:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [2](#0-1) 

uses integer (floor) division. The condition for `rsETHAmount == 0` is:

```
amountAfterFee * 1e18 < rsETHToETHrate
```

rsETH accrues yield, so `rsETHToETHrate` is always `> 1e18` in production. Therefore, for any deposit where `amountAfterFee < rsETHToETHrate / 1e18` (i.e., `amountAfterFee < ~1` for a rate near `1.05e18`), `rsETHAmount` rounds to 0. Concretely, a deposit of **1 wei** with `feeBps = 0` always produces `rsETHAmount = 0` because `1 * 1e18 / 1.05e18 = 0`.

OpenZeppelin's `_mint(to, 0)` does not revert — it is a no-op. The `wrsETH.mint` interface:

```solidity
function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
    _mint(_to, _amount);
}
``` [3](#0-2) 

completes successfully with `_amount = 0`, so `deposit()` returns without reverting. The ETH is now held by the pool.

The only ETH-withdrawal path available to non-admin users is none — `moveAssetsForBridging()` is gated to `BRIDGER_ROLE` and sends funds to the bridger, not back to the depositor:

```solidity
function moveAssetsForBridging() external nonReentrant onlyRole(BRIDGER_ROLE) {
    uint256 ethBalanceMinusFees = address(this).balance - feeEarnedInETH;
    (bool success,) = msg.sender.call{ value: ethBalanceMinusFees }("");
    ...
}
``` [4](#0-3) 

---

### Impact Explanation

A user who deposits a dust amount (e.g., 1 wei) loses their ETH: the contract accepts it, emits a `SwapOccurred` event with `rsETHAmount = 0`, and the user receives nothing. The ETH is not permanently destroyed — the bridger can sweep it via `moveAssetsForBridging()` — but the user has no on-chain mechanism to reclaim it. This matches **Medium: Temporary freezing of funds**.

---

### Likelihood Explanation

- No special role or oracle manipulation is required. Any user can call `deposit()` with 1 wei.
- The condition triggers with a **normal, unmanipulated oracle rate** (any rate `> 1e18`, which is always true for rsETH).
- Accidental dust deposits (e.g., from UI rounding, scripted bots, or fuzz testing) are realistic.
- The `feeBps > 0` case makes the threshold slightly higher but does not eliminate the issue.

---

### Recommendation

Add a post-computation zero-amount guard in `deposit()` (or inside `viewSwapRsETHAmountAndFee`):

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
if (rsETHAmount == 0) revert InvalidAmount();
```

This ensures every accepted ETH deposit results in a non-zero wrsETH mint, preserving the invariant.

---

### Proof of Concept

```solidity
// Preconditions:
//   rsETHOracle.getRate() returns 1.05e18 (normal post-yield rate)
//   feeBps = 0
//   Pool is unpaused, wrsETH minter role granted to pool

// Step 1: attacker calls deposit with 1 wei
pool.deposit{value: 1}("ref");

// Step 2: inside viewSwapRsETHAmountAndFee(1):
//   fee = 1 * 0 / 10_000 = 0
//   amountAfterFee = 1
//   rsETHAmount = 1 * 1e18 / 1.05e18 = 0  (integer division)

// Step 3: feeEarnedInETH += 0  (no change)
// Step 4: wrsETH.mint(attacker, 0)  → succeeds, mints nothing
// Step 5: pool.balance increased by 1 wei, attacker wrsETH balance unchanged

// Assertions:
assert(wrsETH.balanceOf(attacker) == 0);
assert(address(pool).balance == 1);
// attacker has no function to call to recover the 1 wei
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
