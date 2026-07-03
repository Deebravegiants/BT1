### Title
Unvalidated `feeBps` in `initialize()` Allows Fee Exceeding 100%, Causing Depositor Fund Loss or DoS - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
Multiple L2 pool contracts accept an arbitrary `_feeBps` value in their `initialize()` function with no upper-bound check, while the corresponding `setFeeBps()` setter enforces a strict cap. If `feeBps` is initialized at or above 10 000 (100%), every depositor either receives zero wrsETH for their ETH/tokens (complete fund loss) or has their transaction revert (DoS), depending on the exact value.

### Finding Description
In `RSETHPoolV3.sol`, `initialize()` stores `_feeBps` directly:

```solidity
// contracts/pools/RSETHPoolV3.sol  line 229
feeBps = _feeBps;   // no upper-bound check
``` [1](#0-0) 

Yet the post-deployment setter enforces a tight cap of 1 000 BPS (10 %):

```solidity
// contracts/pools/RSETHPoolV3.sol  line 518-521
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_feeBps > 1000) revert InvalidFeeAmount();
    feeBps = _feeBps;
``` [2](#0-1) 

The fee is applied in `viewSwapRsETHAmountAndFee()`:

```solidity
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;   // underflows if feeBps > 10 000
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [3](#0-2) 

The same missing validation exists in every other pool variant:

| Contract | `initialize()` line | `setFeeBps()` cap |
|---|---|---|
| `RSETHPoolV3.sol` | 229 | 1 000 BPS |
| `RSETHPoolNoWrapper.sol` | 214 | 10 000 BPS |
| `RSETHPoolV3WithNativeChainBridge.sol` | 266 | (same pattern) |
| `RSETHPoolV2.sol` | 196 | 10 000 BPS |
| `RSETHPoolV2ExternalBridge.sol` | 278 | 10 000 BPS |
| `RSETHPoolV2NBA.sol` | 95 | 10 000 BPS |
| `AGETHPoolV3.sol` | 98 | 10 000 BPS | [4](#0-3) [5](#0-4) [6](#0-5) 

### Impact Explanation
Two distinct bad outcomes depending on the misconfigured value:

1. **`feeBps == 10 000`** — `fee == amount`, `amountAfterFee == 0`, `rsETHAmount == 0`. Every depositor sends ETH/tokens and receives zero wrsETH. The entire deposit is silently captured as protocol fee and later withdrawn by the BRIDGER role. This is direct theft of depositor funds (Critical).

2. **`feeBps > 10 000`** — `amountAfterFee = amount - fee` underflows and reverts in Solidity 0.8. Every call to `deposit()` reverts, permanently blocking the pool until the admin calls `setFeeBps()` with a corrected value. This is a temporary freeze of depositor funds (Medium).

### Likelihood Explanation
Low. The misconfiguration must occur at deployment time (or via a proxy upgrade that re-runs initialization). It requires either a deployment script error or a malicious deployer — the same threat model explicitly acknowledged in the referenced external report ("requires a configuration error or a malicious actor"). The inconsistency between `initialize()` (no cap) and `setFeeBps()` (hard cap) makes an accidental off-by-one or unit error plausible.

### Recommendation
Add the same upper-bound guard used in `setFeeBps()` to every `initialize()` function:

```solidity
// RSETHPoolV3.sol — initialize()
if (_feeBps > 1000) revert InvalidFeeAmount();
feeBps = _feeBps;
```

Apply the analogous check (using the contract-specific cap) to `RSETHPoolNoWrapper`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolV2`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV2NBA`, and `AGETHPoolV3`.

### Proof of Concept
1. Deploy `RSETHPoolV3` with `_feeBps = 10_000`.
2. Any user calls `deposit{value: 1 ether}("ref")`.
3. `viewSwapRsETHAmountAndFee(1e18)` computes `fee = 1e18 * 10_000 / 10_000 = 1e18`, `amountAfterFee = 0`, `rsETHAmount = 0`.
4. `wrsETH.mint(msg.sender, 0)` is called — user receives nothing.
5. `feeEarnedInETH += 1e18` — the full deposit is recorded as fee.
6. BRIDGER calls `withdrawFees(receiver)` and collects the 1 ETH. [7](#0-6) [3](#0-2)

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

**File:** contracts/pools/RSETHPoolV3.sol (L516-522)
```text
    /// @dev Sets the fee basis points
    /// @param _feeBps The fee basis points
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L190-217)
```text
    function initialize(
        address admin,
        address manager,
        address _rsETH,
        uint256 _feeBps,
        address _rsETHOracle,
        bool _isEthDepositEnabled
    )
        external
        initializer
    {
        UtilLib.checkNonZeroAddress(admin);
        UtilLib.checkNonZeroAddress(manager);
        UtilLib.checkNonZeroAddress(_rsETH);
        UtilLib.checkNonZeroAddress(_rsETHOracle);

        __AccessControl_init();
        __Pausable_init();
        __ReentrancyGuard_init();

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(BRIDGER_ROLE, manager);

        rsETH = IERC20(_rsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
        isEthDepositEnabled = _isEthDepositEnabled;
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
