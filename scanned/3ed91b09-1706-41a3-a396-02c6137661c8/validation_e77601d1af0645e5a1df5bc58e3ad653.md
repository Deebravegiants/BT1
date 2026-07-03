### Title
`feeBps` Set Without Upper-Bound Validation in `initialize()` While `setFeeBps()` Enforces a Hard Cap - (File: contracts/pools/RSETHPoolV3.sol)

---

### Summary

`RSETHPoolV3.initialize()` accepts `_feeBps` and stores it directly without any bounds check, while the post-deployment setter `setFeeBps()` enforces a hard cap of 1000 bps (10%). A deployment with `feeBps = 10_000` (100%) causes every depositor to receive 0 rsETH while their entire ETH/token deposit accumulates as protocol fees, which the BRIDGER_ROLE can then drain via `withdrawFees()`.

---

### Finding Description

`RSETHPoolV3.initialize()` stores `feeBps` without validation:

```solidity
// contracts/pools/RSETHPoolV3.sol L207-232
function initialize(..., uint256 _feeBps, ...) external initializer {
    ...
    feeBps = _feeBps;   // ← no bounds check
    ...
}
```

The post-deployment setter enforces a strict cap:

```solidity
// contracts/pools/RSETHPoolV3.sol L518-522
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_feeBps > 1000) revert InvalidFeeAmount();   // ← max 10%
    feeBps = _feeBps;
}
```

The fee is applied in `viewSwapRsETHAmountAndFee()`:

```solidity
// contracts/pools/RSETHPoolV3.sol L299-308
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
```

If `feeBps = 10_000` at initialization: `fee = amount`, `amountAfterFee = 0`, `rsETHAmount = 0`. Every depositor receives 0 rsETH while their full deposit is credited to `feeEarnedInETH` / `feeEarnedInToken[token]`.

The same pattern exists in `AGETHPoolV3.initialize()` (no check; setter allows up to 10,000 bps) and `RSETHPoolNoWrapper.initialize()` (no check; setter allows up to 10,000 bps), but the inconsistency is most severe in `RSETHPoolV3` where the setter cap is 1,000 bps while the initializer is uncapped.

---

### Impact Explanation

With `feeBps = 10_000` set at initialization:

1. Any user calling `deposit()` (ETH or supported token) receives `rsETHAmount = 0` — their full deposit is silently consumed as fee.
2. `feeEarnedInETH` / `feeEarnedInToken[token]` accumulates the full deposited value.
3. The BRIDGER_ROLE calls `withdrawFees(receiver)` to extract all accumulated funds.

This constitutes **direct theft of all depositor funds** — Critical impact per the allowed scope.

---

### Likelihood Explanation

Low likelihood. The misconfiguration must occur at deployment time (either operational mistake or malicious deployer). Once set, `feeBps` cannot be corrected above 1,000 bps via `setFeeBps()` — but the damage is already done for any deposits made before detection. The inconsistency between the initializer (unchecked) and the setter (capped at 1,000 bps) is the root cause, directly analogous to the ForkDAODeployer pattern in the reference report.

---

### Recommendation

Apply the same upper-bound check in `initialize()` that `setFeeBps()` enforces:

```solidity
function initialize(..., uint256 _feeBps, ...) external initializer {
    if (_feeBps > 1000) revert InvalidFeeAmount();   // match setFeeBps cap
    ...
    feeBps = _feeBps;
}
```

Apply the equivalent fix to `AGETHPoolV3.initialize()` and `RSETHPoolNoWrapper.initialize()` (cap at 10,000 bps to match their respective setters, or tighten to a safer bound).

---

### Proof of Concept

1. Deploy `RSETHPoolV3` proxy and call `initialize(..., _feeBps = 10_000, ...)`.
2. `feeBps` is stored as `10_000`; no revert occurs.
3. User calls `deposit{value: 1 ether}("ref")`.
4. `viewSwapRsETHAmountAndFee(1 ether)` returns `fee = 1 ether`, `rsETHAmount = 0`.
5. `feeEarnedInETH += 1 ether`; `wrsETH.mint(user, 0)` — user receives nothing.
6. BRIDGER_ROLE calls `withdrawFees(attacker)` — 1 ether transferred to attacker.
7. `setFeeBps(10_000)` would revert with `InvalidFeeAmount`, confirming the initializer bypass. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L207-232)
```text
    function initialize(
        address admin,
        address bridger,
        address _wrsETH,
        uint256 _feeBps,
        address _rsETHOracle,
        bool _isEthDepositEnabled
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
        _setupRole(BRIDGER_ROLE, bridger);

        wrsETH = IERC20WrsETH(_wrsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
        isEthDepositEnabled = _isEthDepositEnabled;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
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

**File:** contracts/pools/RSETHPoolV3.sol (L518-522)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```
