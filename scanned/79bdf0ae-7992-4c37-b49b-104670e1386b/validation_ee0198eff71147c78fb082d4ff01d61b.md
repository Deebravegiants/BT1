### Title
Missing Zero Address Check for `admin` in `initialize()` Permanently Breaks Deposits and Bridging - (File: contracts/pools/RSETHPoolV2.sol)

### Summary
`RSETHPoolV2.initialize()` does not validate that `admin` is non-zero before granting `DEFAULT_ADMIN_ROLE`. If `admin` is mistakenly set to `address(0)`, no account will ever hold `DEFAULT_ADMIN_ROLE`, making both `reinitialize` upgrade functions permanently uncallable. Because `dailyMintLimit` defaults to `0` and is only settable via a `reinitialize` that requires `DEFAULT_ADMIN_ROLE`, every subsequent user deposit reverts with `DailyMintLimitExceeded`, permanently freezing the pool's deposit path and all ETH held within it.

### Finding Description
`RSETHPoolV2.initialize()` checks `_wrsETH` and `_rsETHOracle` for zero address via `UtilLib.checkNonZeroAddress`, but applies no such check to `admin` or `bridger`:

```solidity
// contracts/pools/RSETHPoolV2.sol  lines 186-197
UtilLib.checkNonZeroAddress(_wrsETH);
UtilLib.checkNonZeroAddress(_rsETHOracle);
// ...
_grantRole(DEFAULT_ADMIN_ROLE, admin);   // admin unchecked
_setupRole(BRIDGER_ROLE, admin);
_setupRole(BRIDGER_ROLE, bridger);       // bridger unchecked
``` [1](#0-0) 

If `admin == address(0)`, `DEFAULT_ADMIN_ROLE` is granted exclusively to `address(0)`. Both `reinitialize` overloads are gated on `onlyRole(DEFAULT_ADMIN_ROLE)`:

```solidity
// reinitializer(2) – sets l2Bridge / l1VaultETHForL2Chain / messenger
function reinitialize(...) external reinitializer(2) onlyRole(DEFAULT_ADMIN_ROLE) { ... }

// reinitializer(3) – sets dailyMintLimit / startTimestamp
function reinitialize(...) external reinitializer(3) onlyRole(DEFAULT_ADMIN_ROLE) { ... }
``` [2](#0-1) [3](#0-2) 

Neither can ever be called. Consequently:

1. `dailyMintLimit` remains `0` (its default). The `limitDailyMint` modifier enforces `dailyMintAmount + rsETHAmount > dailyMintLimit`, which is `rsETHAmount > 0` — always true for any non-zero deposit — so every call to `deposit()` reverts with `DailyMintLimitExceeded`. [4](#0-3) 

2. `l2Bridge`, `l1VaultETHForL2Chain`, and `messenger` remain `address(0)`. `bridgeAssetsViaNativeBridge()` calls `UtilLib.checkNonZeroAddress` on all three, so bridging ETH to L1 also permanently reverts.

The same pattern exists in `RSETHPoolV2ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`, and `RSETHPoolV2NBA.sol`, all of which omit zero-address validation for `admin` and `bridger` in their `initialize` functions. [5](#0-4) [6](#0-5) [7](#0-6) 

### Impact Explanation
If `admin` is set to `address(0)` at initialization:
- All user deposits revert permanently (`DailyMintLimitExceeded`) because `dailyMintLimit` can never be set.
- All ETH already held in the pool can never be bridged to L1 because bridge addresses can never be set.
- No role management is possible; the contract is permanently unmanageable.

This constitutes **permanent freezing of funds** (ETH held in the pool) and **permanent freezing of unclaimed yield** (accumulated `feeEarnedInETH` cannot be routed correctly without admin control).

### Likelihood Explanation
The likelihood is low but non-negligible. The deployer must pass `address(0)` as `admin`. The original C4 report was accepted at Medium for the same class of mistake. The absence of a guard makes the mistake possible with no on-chain safety net, and the consequence is irreversible because `initializer` can only run once and no recovery path exists without `DEFAULT_ADMIN_ROLE`.

### Recommendation
Add `UtilLib.checkNonZeroAddress` for both `admin` and `bridger` at the top of every affected `initialize` function, consistent with the pattern already used in `KernelDepositPool.initialize`, `KernelReceiver.initialize`, and `KernelVaultETH.initialize`:

```solidity
function initialize(
    address admin,
    address bridger,
    address _wrsETH,
    uint256 _feeBps,
    address _rsETHOracle
) external initializer {
+   UtilLib.checkNonZeroAddress(admin);
+   UtilLib.checkNonZeroAddress(bridger);
    UtilLib.checkNonZeroAddress(_wrsETH);
    UtilLib.checkNonZeroAddress(_rsETHOracle);
    ...
}
``` [8](#0-7) 

### Proof of Concept
1. Deploy `RSETHPoolV2` proxy and call `initialize(address(0), bridger, wrsETH, feeBps, oracle)`.
2. Observe `DEFAULT_ADMIN_ROLE` is held only by `address(0)`.
3. Attempt to call `reinitialize(dailyMintLimit, startTimestamp)` from any EOA → reverts (`AccessControl: account ... is missing role`).
4. Attempt `deposit{value: 1 ether}("")` → reverts with `DailyMintLimitExceeded` because `dailyMintLimit == 0`.
5. Attempt `bridgeAssetsViaNativeBridge()` → reverts with `ZeroAddressNotAllowed` because `l2Bridge` was never set.
6. No recovery path exists; the contract is permanently broken.

### Citations

**File:** contracts/pools/RSETHPoolV2.sol (L86-93)
```text

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
```

**File:** contracts/pools/RSETHPoolV2.sol (L127-146)
```text
    function reinitialize(
        uint256 _dailyMintLimit,
        uint256 _startTimestamp
    )
        external
        reinitializer(3)
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        if (_dailyMintLimit == 0) {
            revert InvalidDailyMintLimit();
        }

        // startTimestamp cannot be in the past
        if (block.timestamp > _startTimestamp) {
            revert InvalidStartTimestamp();
        }

        dailyMintLimit = _dailyMintLimit;
        startTimestamp = _startTimestamp;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L152-168)
```text
    function reinitialize(
        address _l2Bridge,
        address _l1VaultETHForL2Chain,
        address _messenger
    )
        external
        reinitializer(2)
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        UtilLib.checkNonZeroAddress(_l2Bridge);
        UtilLib.checkNonZeroAddress(_l1VaultETHForL2Chain);
        UtilLib.checkNonZeroAddress(_messenger);

        l2Bridge = _l2Bridge;
        l1VaultETHForL2Chain = _l1VaultETHForL2Chain;
        messenger = _messenger;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L186-193)
```text
        UtilLib.checkNonZeroAddress(_wrsETH);
        UtilLib.checkNonZeroAddress(_rsETHOracle);
        __ERC20_init("rsETH", "rsETH");
        __AccessControl_init();
        __ReentrancyGuard_init();
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L258-279)
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
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L245-267)
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L259-262)
```text
    function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
        UtilLib.checkNonZeroAddress(_admin);
        UtilLib.checkNonZeroAddress(_kernelToken);
        UtilLib.checkNonZeroAddress(_rewardToken);
```
