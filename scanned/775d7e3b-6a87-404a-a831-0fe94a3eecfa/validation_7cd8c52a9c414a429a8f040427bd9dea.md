### Title
Instant 100% Fee Setting Without Timelock Allows Admin to Drain All User Deposits - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol)

### Summary
`RSETHPoolV3ExternalBridge.sol` allows `DEFAULT_ADMIN_ROLE` to instantly set `feeBps` up to 10,000 (100%) with no timelock and no on-chain delay, while the same function in `RSETHPoolV3.sol` caps the fee at 1,000 bps (10%). A depositor who calls `deposit()` after a fee change to 100% receives 0 `wrsETH` for their ETH, with the full deposit amount captured as `feeEarnedInETH` and immediately withdrawable by `BRIDGER_ROLE`.

### Finding Description
`RSETHPoolV3ExternalBridge.setFeeBps` is gated only by `DEFAULT_ADMIN_ROLE` and enforces a ceiling of 10,000 bps (100%):

```solidity
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_feeBps > 10_000) revert InvalidFeeAmount();   // 100% allowed
    feeBps = _feeBps;
    emit FeeBpsSet(_feeBps);
}
``` [1](#0-0) 

The sister contract `RSETHPoolV3.sol` caps the same parameter at 1,000 bps (10%):

```solidity
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_feeBps > 1000) revert InvalidFeeAmount();     // 10% cap
    feeBps = _feeBps;
    emit FeeBpsSet(_feeBps);
}
``` [2](#0-1) 

The fee is applied in `viewSwapRsETHAmountAndFee` before computing the `wrsETH` amount to mint:

```solidity
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [3](#0-2) 

When `feeBps == 10_000`, `amountAfterFee == 0`, so `rsETHAmount == 0`. The full deposit is credited to `feeEarnedInETH`:

```solidity
feeEarnedInETH += fee;
wrsETH.mint(msg.sender, rsETHAmount);   // mints 0
``` [4](#0-3) 

`feeEarnedInETH` is immediately withdrawable by `BRIDGER_ROLE` via `withdrawFees`:

```solidity
function withdrawFees(address receiver) external nonReentrant onlyRole(BRIDGER_ROLE) {
    uint256 amountToSendInETH = feeEarnedInETH;
    feeEarnedInETH = 0;
    (bool success,) = payable(receiver).call{ value: amountToSendInETH }("");
``` [5](#0-4) 

The protocol does define a `TIMELOCK_ROLE` and uses it for oracle and bridge address changes, but deliberately omits it for `setFeeBps`, meaning the fee change takes effect in the same block it is submitted with no user-observable delay: [6](#0-5) 

### Impact Explanation
Any user who calls `deposit()` after `feeBps` is set to 10,000 loses 100% of their ETH: they pay ETH into the pool, receive 0 `wrsETH`, and cannot recover the ETH because it is immediately classified as earned fees and withdrawable by `BRIDGER_ROLE`. This constitutes direct theft of user funds in motion. The inconsistency with `RSETHPoolV3.sol`'s 10% cap confirms the 100% ceiling in `RSETHPoolV3ExternalBridge.sol` is an unintended design gap rather than a deliberate choice.

**Impact: Critical — direct theft of user funds in motion.**

### Likelihood Explanation
The `TIMELOCK_ROLE` pattern already exists in the same contract for other sensitive setters (`setRSETHOracle`, `addSupportedToken`, `setL1VaultETHForL2Chain`, etc.), demonstrating the protocol's own intent to gate critical changes behind a delay. The omission of `TIMELOCK_ROLE` on `setFeeBps` — combined with the 100% ceiling — is a concrete, reachable gap. Any depositor who transacts in the same block or shortly after a fee change is directly affected with no ability to front-run or react.

### Recommendation
1. **Align the fee cap** with `RSETHPoolV3.sol`: change the ceiling from `10_000` to `1_000` (10%) in `RSETHPoolV3ExternalBridge.setFeeBps`.
2. **Gate `setFeeBps` behind `TIMELOCK_ROLE`** (already defined in the contract) instead of `DEFAULT_ADMIN_ROLE`, consistent with how other critical setters are protected.
3. Optionally introduce a two-step fee change with a minimum announcement delay so users can observe the pending change and exit before it takes effect.

### Proof of Concept
1. Admin calls `setFeeBps(10_000)` on `RSETHPoolV3ExternalBridge` — transaction succeeds immediately, no timelock.
2. User calls `deposit{value: 1 ether}("ref")` in the next block.
3. `viewSwapRsETHAmountAndFee(1 ether)` computes: `fee = 1e18 * 10_000 / 10_000 = 1e18`, `amountAfterFee = 0`, `rsETHAmount = 0`.
4. `wrsETH.mint(msg.sender, 0)` — user receives nothing.
5. `feeEarnedInETH += 1e18` — 1 ETH is now claimable by `BRIDGER_ROLE` via `withdrawFees`.
6. User has lost 1 ETH with no recourse.

### Citations

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L50-51)
```text
    bytes32 public constant BRIDGER_ROLE = keccak256("BRIDGER_ROLE");
    bytes32 public constant TIMELOCK_ROLE = keccak256("TIMELOCK_ROLE");
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L377-383)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L418-427)
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L617-625)
```text
    function withdrawFees(address receiver) external nonReentrant onlyRole(BRIDGER_ROLE) {
        // withdraw fees in ETH
        uint256 amountToSendInETH = feeEarnedInETH;
        feeEarnedInETH = 0;
        (bool success,) = payable(receiver).call{ value: amountToSendInETH }("");
        if (!success) revert TransferFailed();

        emit FeesWithdrawn(amountToSendInETH);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L742-748)
```text
    /// @dev Sets the fee basis points
    /// @param _feeBps The fee basis points
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L518-522)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```
