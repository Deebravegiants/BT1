### Title
`feeBps` Initialized Without Upper-Bound Validation Present in `setFeeBps()`, Enabling Zero-rsETH Deposits - (File: contracts/pools/RSETHPoolV3.sol, RSETHPoolV3ExternalBridge.sol, RSETHPoolV3WithNativeChainBridge.sol, RSETHPoolV2ExternalBridge.sol, RSETHPoolV2.sol, RSETHPoolNoWrapper.sol, agETH/AGETHPoolV3.sol)

---

### Summary

Across all L2 pool contracts, `feeBps` is assigned in `initialize()` without the upper-bound check that is enforced in `setFeeBps()`. The validation logic is separated from the point of variable assignment, exactly mirroring the Atlendis pattern. If `feeBps` is initialized to `10_000` (100%), every depositor receives `0` rsETH while their ETH/tokens are permanently locked as protocol fees, constituting direct theft of user funds.

---

### Finding Description

Every pool contract exposes a `setFeeBps()` function that enforces an upper-bound cap:

- `RSETHPoolV3.setFeeBps()`: `if (_feeBps > 1000) revert InvalidFeeAmount();`
- `RSETHPoolV3ExternalBridge.setFeeBps()`: `if (_feeBps > 10_000) revert InvalidFeeAmount();`
- `RSETHPoolV3WithNativeChainBridge.setFeeBps()`: `if (_feeBps > 1000) revert InvalidFeeAmount();`
- `RSETHPoolV2ExternalBridge.setFeeBps()`: `if (_feeBps > 1000) revert InvalidFeeAmount();`
- `RSETHPoolNoWrapper.setFeeBps()`: `if (_feeBps > 10_000) revert InvalidFeeAmount();`
- `AGETHPoolV3.setFeeBps()`: `if (_feeBps > 10_000) revert InvalidFeeAmount();` [1](#0-0) 

However, every corresponding `initialize()` function assigns `feeBps = _feeBps` with no such check: [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

The fee calculation in `viewSwapRsETHAmountAndFee()` is:

```solidity
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [7](#0-6) 

When `feeBps == 10_000`: `fee == amount`, `amountAfterFee == 0`, `rsETHAmount == 0`. The depositor's ETH is accepted and credited to `feeEarnedInETH`, but they receive zero rsETH. When `feeBps > 10_000`: `amount - fee` underflows and reverts, freezing all deposits. [8](#0-7) 

---

### Impact Explanation

**Critical — Direct theft of user funds.**

If `feeBps` is initialized to `10_000`, every call to `deposit()` by any unprivileged user results in their ETH or LST being transferred into the pool and permanently credited to `feeEarnedInETH` / `feeEarnedInToken`, while the user receives `0` rsETH. The assets are only withdrawable by the `BRIDGER_ROLE` via `withdrawFees()`, not by the depositor. [9](#0-8) 

---

### Likelihood Explanation

**Low.** The misconfiguration must occur at deployment time by the deployer. However, the pattern is structurally error-prone: a developer who sees `setFeeBps()` enforcing the cap may assume the same invariant holds at initialization. The validation is silently absent from `initialize()` across seven contracts, making the mistake plausible during future deployments or upgrades. This is the exact scenario described in the Atlendis report.

---

### Recommendation

**Short term:** Add the same upper-bound check to every `initialize()` function that sets `feeBps`:

```solidity
if (_feeBps > 1000) revert InvalidFeeAmount(); // match setFeeBps() cap
feeBps = _feeBps;
```

**Long term:** Keep validation logic co-located with every assignment of `feeBps`, whether in `initialize()`, `reinitialize()`, or `setFeeBps()`. Consider extracting a shared internal `_setFeeBps()` function that both paths call, ensuring the invariant is never silently bypassed.

---

### Proof of Concept

1. Deploy `RSETHPoolV3` via its proxy, calling `initialize()` with `_feeBps = 10_000`.
2. No revert occurs — `feeBps` is stored as `10_000`.
3. A user calls `deposit{value: 1 ether}("ref")`.
4. Inside `viewSwapRsETHAmountAndFee(1 ether)`:
   - `fee = 1e18 * 10_000 / 10_000 = 1e18`
   - `amountAfterFee = 1e18 - 1e18 = 0`
   - `rsETHAmount = 0`
5. `feeEarnedInETH += 1e18` — the ETH is locked as fees.
6. `wrsETH.mint(msg.sender, 0)` — user receives nothing.
7. The user has permanently lost 1 ETH. Only the `BRIDGER_ROLE` can recover it via `withdrawFees()`. [10](#0-9) [7](#0-6)

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

**File:** contracts/pools/RSETHPoolV3.sol (L244-265)
```text
    /// @dev Swaps ETH for rsETH
    /// @param referralId The referral id
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
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

**File:** contracts/pools/RSETHPoolV3.sol (L452-461)
```text
    /// @dev Withdraws fees earned by the pool in ETH
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L330-352)
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L245-268)
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

**File:** contracts/agETH/AGETHPoolV3.sol (L76-101)
```text
    function initialize(
        address admin,
        address bridger,
        address _agETH,
        uint256 _feeBps,
        address _agETHOracle
    )
        external
        initializer
    {
        UtilLib.checkNonZeroAddress(_agETH);
        UtilLib.checkNonZeroAddress(_agETHOracle);

        __ERC20_init("agETH", "agETH");
        __AccessControl_init();
        __ReentrancyGuard_init();

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);

        agETH = IERC20AgETH(_agETH);
        feeBps = _feeBps;
        agETHOracle = _agETHOracle;
        isEthDepositEnabled = true;
    }
```
