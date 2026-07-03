### Title
Unvalidated `_feeBps` in `initialize()` Bypasses Protocol Fee Cap, Enabling Depositor Fund Loss - (File: contracts/pools/RSETHPoolV3.sol)

---

### Summary
The `initialize()` function in `RSETHPoolV3` (and sibling pool variants) accepts `_feeBps` without any upper bound check, while the post-deployment setter `setFeeBps()` enforces a hard cap of 1000 bps (10%). If `feeBps` is initialized at 10 000 (100%), every depositor receives 0 rsETH and their entire deposit is silently captured as protocol fees.

---

### Finding Description

`RSETHPoolV3.initialize()` assigns `feeBps` directly with no validation:

```solidity
// contracts/pools/RSETHPoolV3.sol  lines 228-229
wrsETH = IERC20WrsETH(_wrsETH);
feeBps = _feeBps;          // ← no upper-bound check
``` [1](#0-0) 

The post-deployment setter enforces a strict cap:

```solidity
// contracts/pools/RSETHPoolV3.sol  line 519
if (_feeBps > 1000) revert InvalidFeeAmount();
``` [2](#0-1) 

The fee arithmetic used on every deposit is:

```solidity
// contracts/pools/RSETHPoolV3.sol  lines 300-307
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [3](#0-2) 

When `feeBps = 10 000`:
- `fee = amount * 10 000 / 10 000 = amount`
- `amountAfterFee = amount − amount = 0`
- `rsETHAmount = 0 * 1e18 / rate = 0`

The depositor receives **0 rsETH**; the full deposit is added to `feeEarnedInETH` and becomes withdrawable by the `BRIDGER_ROLE` via `withdrawFees()`.

When `feeBps > 10 000`:
- `fee > amount` → `amountAfterFee` underflows → every `deposit()` call reverts → pool is permanently bricked for depositors.

The identical gap exists in three additional pool initializers that also assign `feeBps = _feeBps` without validation: [4](#0-3) [5](#0-4) [6](#0-5) 

---

### Impact Explanation

**Critical – Direct theft of user funds.**  
With `feeBps = 10 000`, every depositor loses 100 % of their ETH or LST deposit. The stolen value accumulates in `feeEarnedInETH` / `feeEarnedInToken` and is extractable by the `BRIDGER_ROLE` through `withdrawFees()`. No depositor can recover their principal.

With `feeBps > 10 000`, all `deposit()` calls revert permanently, constituting a permanent freeze of the pool.

---

### Likelihood Explanation

**Low.**  
Exploitation requires the deployer/admin to supply an out-of-range `_feeBps` during initialization — either through misconfiguration (e.g., supplying a raw percentage `100` instead of basis points `100`, or accidentally supplying `10000` meaning "100 %") or through a malicious deployment. The inconsistency between `initialize()` (no cap) and `setFeeBps()` (cap = 1000) makes accidental misconfiguration plausible, particularly across the multiple pool variants that share the same pattern.

---

### Recommendation

Apply the same upper-bound guard in every `initialize()` that sets `feeBps`:

```solidity
if (_feeBps > 1000) revert InvalidFeeAmount();
feeBps = _feeBps;
```

This mirrors the existing protection in `setFeeBps()` and closes the inconsistency across `RSETHPoolV3`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, and `RSETHPoolNoWrapper`.

---

### Proof of Concept

1. Deploy `RSETHPoolV3` proxy; call `initialize(admin, bridger, wrsETH, 10_000, oracle, true)`.
2. Any user calls `deposit{value: 1 ether}("ref")`.
3. Inside `viewSwapRsETHAmountAndFee(1e18)`:
   - `fee = 1e18 * 10_000 / 10_000 = 1e18`
   - `amountAfterFee = 1e18 − 1e18 = 0`
   - `rsETHAmount = 0`
4. `wrsETH.mint(msg.sender, 0)` — user receives **zero** rsETH.
5. `feeEarnedInETH += 1e18` — the full 1 ETH is now claimable as fees.
6. `BRIDGER_ROLE` calls `withdrawFees(attacker)` to drain the stolen ETH. [7](#0-6)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L228-229)
```text
        wrsETH = IERC20WrsETH(_wrsETH);
        feeBps = _feeBps;
```

**File:** contracts/pools/RSETHPoolV3.sol (L300-307)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3.sol (L453-461)
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

**File:** contracts/pools/RSETHPoolV3.sol (L518-521)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L277-279)
```text
        wrsETH = IERC20WrsETH(_wrsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L265-267)
```text
        wrsETH = IERC20WrsETH(_wrsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L213-215)
```text
        rsETH = IERC20(_rsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
```
