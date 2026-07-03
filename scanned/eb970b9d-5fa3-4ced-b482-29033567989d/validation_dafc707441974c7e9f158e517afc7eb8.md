The vulnerability is real and concrete. Here is the full analysis:

---

### Title
Zero-Output Deposit Silently Consumes ETH Without Minting wrsETH - (`contracts/pools/RSETHPoolV2NBA.sol`)

### Summary
`deposit()` in `RSETHPoolV2NBA` only guards against `amount == 0` but does not guard against `rsETHAmount == 0` after the fee-and-rate division. When a depositor sends a small ETH amount, integer truncation in `viewSwapRsETHAmountAndFee` can produce `rsETHAmount = 0`. OpenZeppelin's `_mint` does not revert on a zero amount, so the transaction succeeds: the ETH is retained in the pool, the depositor receives nothing, and no error is raised.

### Finding Description

In `RSETHPoolV2NBA.deposit()`:

```solidity
// contracts/pools/RSETHPoolV2NBA.sol  lines 106-118
function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();          // only zero-amount guard
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);             // rsETHAmount may be 0
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
``` [1](#0-0) 

The rate calculation in `viewSwapRsETHAmountAndFee` uses plain integer division:

```solidity
// contracts/pools/RSETHPoolV2NBA.sol  lines 124-133
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;   // truncates to 0
}
``` [2](#0-1) 

The `wrsETH.mint` implementation (via `RsETHTokenWrapper`) delegates to OpenZeppelin's `_mint`, which only checks `account != address(0)` — it does **not** revert on `amount == 0`:

```solidity
// contracts/L2/RsETHTokenWrapper.sol  line 190-192
function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
    _mint(_to, _amount);   // succeeds silently with _amount == 0
}
``` [3](#0-2) 

```solidity
// lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol  line 251-252
function _mint(address account, uint256 amount) internal virtual {
    require(account != address(0), "ERC20: mint to the zero address");  // only guard
``` [4](#0-3) 

### Impact Explanation

**Temporary freezing of user funds.** The depositor's ETH is accepted by the contract, `feeEarnedInETH` is incremented by `fee` (which is also 0 for 1-wei deposits), and the ETH sits untracked in the contract balance. The depositor holds no wrsETH and has no mechanism to reclaim the ETH. The ETH will eventually be swept to L1 by the bridger via `moveAssetsForBridging()` (which sends `address(this).balance - feeEarnedInETH`), permanently removing the depositor's claim. [5](#0-4) 

### Likelihood Explanation

The preconditions are entirely user-controlled and require no special role or privileged access:
- `feeBps > 0` — normal production configuration.
- `amount` small enough that `amountAfterFee * 1e18 < rsETHToETHrate` — with a typical rate of `~1.05e18`, any deposit of 1 wei satisfies this. Even with `feeBps = 0`, a 1-wei deposit yields `rsETHAmount = 0`.

Any user who accidentally (or deliberately) sends a dust ETH amount triggers this path. The transaction emits a `SwapOccurred` event with `rsETHAmount = 0`, which may mislead off-chain monitoring into treating it as a successful swap.

### Recommendation

Add a post-calculation guard in `deposit()`:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
if (rsETHAmount == 0) revert InvalidAmount();
```

This ensures the invariant: any accepted ETH deposit produces a non-zero wrsETH amount, or the transaction reverts and the ETH is returned to the caller.

### Proof of Concept

Concrete arithmetic with `feeBps = 100`, `rsETHToETHrate = 1.05e18`, `amount = 1 wei`:

```
fee          = 1 * 100 / 10_000 = 0
amountAfterFee = 1 - 0          = 1
rsETHAmount  = 1 * 1e18 / 1.05e18 = 0   ← truncated
```

`wrsETH.mint(msg.sender, 0)` succeeds. The depositor loses 1 wei with no wrsETH issued and no revert. The minimum safe deposit threshold (with `feeBps = 0`) is `ceil(rsETHToETHrate / 1e18)` wei — i.e., at least 2 wei when the rate is `1.05e18`. With any non-zero `feeBps`, the threshold is slightly higher.

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

**File:** contracts/pools/RSETHPoolV2NBA.sol (L151-159)
```text
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

**File:** lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol (L251-252)
```text
    function _mint(address account, uint256 amount) internal virtual {
        require(account != address(0), "ERC20: mint to the zero address");
```
