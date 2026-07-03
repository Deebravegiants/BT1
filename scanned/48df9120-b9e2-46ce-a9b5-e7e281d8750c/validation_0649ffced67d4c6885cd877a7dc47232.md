### Title
`setFeeBps` Permits 100% Fee Setting, Causing Depositors to Receive Zero wrsETH/agETH - (File: `contracts/pools/RSETHPool.sol`)

---

### Summary

Multiple L2 pool contracts allow `feeBps` to be set to `10_000` (100%), which causes any depositor to receive zero wrapped tokens while their entire ETH or LST deposit is silently absorbed as protocol fee.

---

### Finding Description

The `setFeeBps` function in `RSETHPool.sol`, `RSETHPoolNoWrapper.sol`, `RSETHPoolV2.sol`, `RSETHPoolV2NBA.sol`, and `AGETHPoolV3.sol` enforces only an upper bound of `10_000` (100% in basis points):

```solidity
// RSETHPool.sol
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_feeBps > 10_000) revert InvalidFeeAmount();   // allows exactly 10_000
    feeBps = _feeBps;
    emit FeeBpsSet(_feeBps);
}
```

When `feeBps == 10_000`, the fee calculation in `viewSwapRsETHAmountAndFee` / `viewSwapAgETHAmountAndFee` produces:

```
fee           = amount * 10_000 / 10_000  = amount
amountAfterFee = amount - fee             = 0
rsETHAmount   = 0 * 1e18 / rsETHToETHrate = 0
```

The deposit function then executes `safeTransfer(msg.sender, 0)` (RSETHPool) or `mint(msg.sender, 0)` (RSETHPoolV2, AGETHPoolV3) — both succeed silently — while `feeEarnedInETH += amount` records the entire deposit as fee.

There is no `minRSETHAmountExpected` guard in any of these deposit paths, so the transaction completes without revert and the user receives nothing.

The inconsistency is confirmed by the newer pool variants: `RSETHPoolV3`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge` all cap `feeBps` at `1_000` (10%):

```solidity
// RSETHPoolV3.sol
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_feeBps > 1000) revert InvalidFeeAmount();   // correct cap
    ...
}
```

This demonstrates the `10_000` ceiling in the older contracts is an oversight, not intentional design.

The same root cause applies to `setTokenFeeBps` in `RSETHPool.sol`, which also allows `_feeBps == 10_000` for per-token fee overrides used in the token deposit path.

---

### Impact Explanation

Any user calling `deposit()` on an affected pool while `feeBps == 10_000` deposits ETH or LSTs and receives **zero** wrsETH/agETH in return. Their full deposit is retained by the pool as fee and is later withdrawable only by the `BRIDGER_ROLE` via `withdrawFees`. This is direct theft of depositor funds.

**Impact: High — theft of depositor funds (ETH/LST in motion).**

---

### Likelihood Explanation

Low. Requires the `DEFAULT_ADMIN_ROLE` holder to set `feeBps` to `10_000` — either through a configuration error (e.g., confusing basis points with percentage points, or copy-pasting from a contract that uses a different denominator) or through malicious/compromised admin action. This is directly analogous to the external report's governance configuration-error scenario for `GaugeProxy::setValidatorFee`.

---

### Recommendation

Cap `feeBps` at a sensible maximum in all affected contracts, consistent with the newer pool variants:

```solidity
// Replace in RSETHPool.sol, RSETHPoolNoWrapper.sol, RSETHPoolV2.sol,
// RSETHPoolV2NBA.sol, AGETHPoolV3.sol
if (_feeBps > 1_000) revert InvalidFeeAmount(); // max 10%
```

Apply the same fix to `setTokenFeeBps` in `RSETHPool.sol`.

---

### Proof of Concept

1. Admin calls `RSETHPool.setFeeBps(10_000)` — passes validation (`10_000 > 10_000` is false).
2. User calls `RSETHPool.deposit{value: 1 ether}("ref")`.
3. `viewSwapRsETHAmountAndFee(1 ether)` → `fee = 1 ether`, `rsETHAmount = 0`.
4. `feeEarnedInETH += 1 ether` — pool records the full deposit as fee.
5. `IERC20(wrsETH).safeTransfer(msg.sender, 0)` — succeeds, user receives 0 wrsETH.
6. Bridger later calls `withdrawFees(receiver)` and extracts the user's 1 ETH.

The same sequence applies to `AGETHPoolV3.deposit()` (mints 0 agETH) and to the token deposit path via `setTokenFeeBps(token, 10_000)`.

---

**Affected files and lines:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8)

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

**File:** contracts/pools/RSETHPool.sol (L574-578)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```

**File:** contracts/pools/RSETHPool.sol (L583-594)
```text
    function setTokenFeeBps(
        address token,
        uint256 _feeBps
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
        onlySupportedToken(token)
    {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        tokenFeeBps[token] = _feeBps;
        emit TokenFeeBpsSet(token, _feeBps);
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L303-307)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(TIMELOCK_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L163-167)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L160-168)
```text
    function viewSwapAgETHAmountAndFee(uint256 amount) public view returns (uint256 agETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of agETH in ETH
        uint256 agETHToETHrate = getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * 1e18 / agETHToETHrate;
```

**File:** contracts/agETH/AGETHPoolV3.sol (L245-251)
```text
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
