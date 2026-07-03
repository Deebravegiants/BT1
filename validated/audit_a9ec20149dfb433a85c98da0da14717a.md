### Title
`feeBps` Lacks Upper-Bound Validation in `initialize` While `setFeeBps` Enforces It — (`contracts/agETH/AGETHPoolV3.sol`, `contracts/pools/RSETHPool.sol`, `contracts/pools/RSETHPoolNoWrapper.sol`, `contracts/pools/RSETHPoolV2NBA.sol`, `contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`, `contracts/pools/RSETHPoolV2ExternalBridge.sol`)

---

### Summary

Multiple pool contracts expose a `feeBps` parameter during `initialize` that is stored without any upper-bound check. The corresponding `setFeeBps` admin function in every one of these contracts enforces `_feeBps > 10_000 → revert InvalidFeeAmount()`. If `feeBps` is initialized above 10,000, every subsequent user deposit reverts due to arithmetic underflow in `viewSwapRsETHAmountAndFee` / `viewSwapAgETHAmountAndFee`, temporarily freezing all rsETH/agETH tokens pre-loaded in the pool.

---

### Finding Description

Every affected pool contract stores the fee parameter during initialization without validation:

**`AGETHPoolV3.sol` — `initialize`** (line 98):
```solidity
feeBps = _feeBps;   // no upper-bound check
``` [1](#0-0) 

But `setFeeBps` enforces the bound:
```solidity
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_feeBps > 10_000) revert InvalidFeeAmount();
    feeBps = _feeBps;
``` [2](#0-1) 

The same pattern exists in:

- `RSETHPool.sol` `initialize` line 248 vs `setFeeBps` line 574–575 [3](#0-2) [4](#0-3) 

- `RSETHPoolNoWrapper.sol` `initialize` line 214 vs `setFeeBps` line 524–525 [5](#0-4) 

- `RSETHPoolV2NBA.sol` `initialize` line 95 vs `setFeeBps` line 163–164 [6](#0-5) [7](#0-6) 

- `RSETHPoolV3.sol` `initialize` line 229 vs `setFeeBps` line 518–519 (cap is 1,000 there) [8](#0-7) [9](#0-8) 

- `RSETHPoolV3WithNativeChainBridge.sol` `initialize` line 266 [10](#0-9) 

- `RSETHPoolV2ExternalBridge.sol` `initialize` line 278 [11](#0-10) 

The fee is consumed in `viewSwapAgETHAmountAndFee` / `viewSwapRsETHAmountAndFee`:

```solidity
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;   // underflows if feeBps > 10_000
``` [12](#0-11) [13](#0-12) 

In Solidity 0.8+, `amount - fee` reverts on underflow when `feeBps > 10,000`.

---

### Impact Explanation

If `feeBps` is initialized above 10,000 (e.g., 10,001 or higher due to a decimal-unit mistake such as entering `100_000` instead of `1_000`):

1. Every call to `deposit` invokes `viewSwapRsETHAmountAndFee` / `viewSwapAgETHAmountAndFee`.
2. `fee = amount * feeBps / 10_000 > amount` → `amount - fee` underflows → revert.
3. All user deposits are permanently blocked until an admin calls `setFeeBps` with a corrected value.
4. rsETH/agETH tokens pre-loaded in the pool by the bridger are temporarily frozen and inaccessible to depositors.

**Impact: Medium — Temporary freezing of funds.**

---

### Likelihood Explanation

The `initialize` function is called exactly once per proxy deployment. There is no on-chain guard preventing `_feeBps > 10_000`. A deployer who confuses basis-point scale (e.g., enters `100_000` for "10%" instead of `1_000`) silently deploys a broken pool. The setter `setFeeBps` would have caught this, but it is never called during initialization. This is the same class of human error described in the reference report.

**Likelihood: Low** (requires admin deployment error, but the missing guard makes it plausible).

---

### Recommendation

Add the same upper-bound guard to every `initialize` function that is already present in the corresponding `setFeeBps`:

```solidity
// In initialize(), before feeBps = _feeBps:
if (_feeBps > 10_000) revert InvalidFeeAmount();
feeBps = _feeBps;
```

For `RSETHPoolV3` and similar contracts where `setFeeBps` caps at 1,000 (10%), use the tighter bound in `initialize` as well.

---

### Proof of Concept

1. Deploy `AGETHPoolV3` (or any affected pool) via its proxy, passing `_feeBps = 20_000` (200%) to `initialize`.
2. Observe: deployment succeeds, `feeBps` is now 20,000.
3. Any user calls `deposit{value: 1 ether}(referralId)`.
4. Inside `viewSwapAgETHAmountAndFee`: `fee = 1e18 * 20_000 / 10_000 = 2e18 > 1e18`; `amountAfterFee = 1e18 - 2e18` → arithmetic underflow → revert.
5. All deposits revert. rsETH/agETH tokens pre-loaded in the pool are inaccessible until admin calls `setFeeBps` with a valid value.
6. Confirm: calling `setFeeBps(20_000)` directly would have reverted with `InvalidFeeAmount`, but `initialize(... 20_000)` did not.

### Citations

**File:** contracts/agETH/AGETHPoolV3.sol (L97-99)
```text
        agETH = IERC20AgETH(_agETH);
        feeBps = _feeBps;
        agETHOracle = _agETHOracle;
```

**File:** contracts/agETH/AGETHPoolV3.sol (L161-162)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/agETH/AGETHPoolV3.sol (L245-248)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();

        feeBps = _feeBps;
```

**File:** contracts/pools/RSETHPool.sol (L248-248)
```text
        feeBps = _feeBps;
```

**File:** contracts/pools/RSETHPool.sol (L574-576)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L214-214)
```text
        feeBps = _feeBps;
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L278-279)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L95-95)
```text
        feeBps = _feeBps;
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L163-164)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
```

**File:** contracts/pools/RSETHPoolV3.sol (L229-229)
```text
        feeBps = _feeBps;
```

**File:** contracts/pools/RSETHPoolV3.sol (L518-519)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L266-266)
```text
        feeBps = _feeBps;
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L278-278)
```text
        feeBps = _feeBps;
```
