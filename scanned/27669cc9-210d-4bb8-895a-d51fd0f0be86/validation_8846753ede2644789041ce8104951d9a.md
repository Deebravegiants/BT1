### Title
`feeBps` Set Without Upper-Bound Validation in `initialize()` While `setFeeBps()` Enforces a Cap - (File: contracts/pools/RSETHPoolV2ExternalBridge.sol, contracts/pools/RSETHPoolV2NBA.sol, contracts/pools/RSETHPoolV2.sol)

---

### Summary

Multiple L2 pool contracts accept a `_feeBps` parameter in their `initialize()` function and assign it directly to `feeBps` with no upper-bound check. The corresponding `setFeeBps()` setter enforces a strict cap (`_feeBps > 10_000`), but this invariant is absent at initialization time. If `_feeBps > 10_000` is supplied during deployment, every subsequent call to `deposit()` will revert due to arithmetic underflow, permanently disabling the deposit path until an admin corrects the value.

---

### Finding Description

**Affected contracts and lines:**

- `RSETHPoolV2ExternalBridge.sol` — `initialize()` lines 258–280, assignment at line 278
- `RSETHPoolV2NBA.sol` — `initialize()` lines 75–97, assignment at line 95
- `RSETHPoolV2.sol` — `initialize()` lines 176+, same pattern

In each contract the setter enforces a cap:

```solidity
// RSETHPoolV2ExternalBridge.sol (and siblings)
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_feeBps > 10_000) revert InvalidFeeAmount();   // ← guard present
    feeBps = _feeBps;
}
```

But the initializer assigns the value unconditionally:

```solidity
// RSETHPoolV2ExternalBridge.sol initialize()
wrsETH = IERC20WrsETH(_wrsETH);
feeBps = _feeBps;          // ← no bounds check
rsETHOracle = _rsETHOracle;
```

The fee is consumed in `viewSwapRsETHAmountAndFee()`:

```solidity
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;   // underflows if feeBps > 10_000
```

If `feeBps > 10_000`, `fee > amount`, and the subtraction reverts under Solidity 0.8 checked arithmetic, making `deposit()` permanently inaccessible until an admin calls `setFeeBps()` with a valid value.

Note: `RSETHPoolV3.sol`'s `setFeeBps()` enforces an even stricter cap of `1_000` (10%), making the initialization gap proportionally wider for that variant.

---

### Impact Explanation

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

If `feeBps` is initialized above `10_000`, every call to `deposit()` reverts. Users cannot swap ETH for `wrsETH`/`rsETH` on the affected L2 pool. Existing balances in the contract are unaffected and no funds are lost; the pool simply cannot accept new deposits until the admin corrects the fee via `setFeeBps()`. This matches the "contract fails to deliver promised returns" category.

---

### Likelihood Explanation

**Likelihood: Low.**

The `initialize()` function is called once by the deployer. A misconfiguration (e.g., passing basis points as a percentage, e.g., `10_500` instead of `105`) is plausible during deployment scripting, especially since the cap is not documented in the function's NatSpec. The absence of a guard means the contract provides no safety net against such an error, unlike every other setter in the same file.

---

### Recommendation

Apply the same upper-bound check inside `initialize()` that is already present in `setFeeBps()`:

```solidity
function initialize(
    address admin,
    address bridger,
    address _wrsETH,
    uint256 _feeBps,
    address _rsETHOracle
) external initializer {
    if (_feeBps > 10_000) revert InvalidFeeAmount();   // add this
    ...
    feeBps = _feeBps;
}
```

For `RSETHPoolV3` variants where `setFeeBps()` caps at `1_000`, use the same tighter bound in the initializer.

---

### Proof of Concept

1. Deploy `RSETHPoolV2ExternalBridge` and call `initialize(admin, bridger, wrsETH, 10_001, oracle)`.
2. `feeBps` is now `10_001`; no revert occurs during initialization.
3. Any user calls `deposit{value: 1 ether}("ref")`.
4. Inside `viewSwapRsETHAmountAndFee(1e18)`:
   - `fee = 1e18 * 10_001 / 10_000 = 1.0001e18`
   - `amountAfterFee = 1e18 - 1.0001e18` → **arithmetic underflow → revert**
5. All deposits are blocked. The pool is non-functional until the admin calls `setFeeBps(validValue)`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L258-280)
```text
    function initialize(
        address admin,
        address bridger,
        address _wrsETH,
        uint256 _feeBps,
        address _rsETHOracle
    )
        external
        initializer
    {
        UtilLib.checkNonZeroAddress(_wrsETH);
        UtilLib.checkNonZeroAddress(_rsETHOracle);
        __ERC20_init("rsETH", "rsETH");
        __AccessControl_init();
        __ReentrancyGuard_init();
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);

        wrsETH = IERC20WrsETH(_wrsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L307-315)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L75-97)
```text
    function initialize(
        address admin,
        address bridger,
        address _wrsETH,
        uint256 _feeBps,
        address _rsETHOracle
    )
        external
        initializer
    {
        UtilLib.checkNonZeroAddress(_wrsETH);
        UtilLib.checkNonZeroAddress(_rsETHOracle);
        __ERC20_init("rsETH", "rsETH");
        __AccessControl_init();
        __ReentrancyGuard_init();
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);

        wrsETH = IERC20WrsETH(_wrsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L518-521)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
```
