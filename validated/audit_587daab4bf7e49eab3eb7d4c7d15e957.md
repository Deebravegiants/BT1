### Title
Missing Zero-Address Validation for `admin` in Initializer Permanently Freezes Admin Control and Fee ETH - (File: contracts/pools/RSETHPoolV2ExternalBridge.sol)

### Summary
`RSETHPoolV2ExternalBridge.initialize()` validates `_wrsETH` and `_rsETHOracle` against zero address but omits the same check for `admin` and `bridger`. If `admin` is supplied as `address(0)` — possible during redeployments on new networks — `DEFAULT_ADMIN_ROLE` is granted to `address(0)`, leaving no real account with admin authority. All subsequent admin-gated operations (fee withdrawal, pausing, reinitializations) become permanently inaccessible, and any ETH fees that accumulate in the contract are permanently frozen.

### Finding Description
`RSETHPoolV2ExternalBridge.initialize()` performs zero-address checks only on `_wrsETH` and `_rsETHOracle`:

```solidity
function initialize(
    address admin,
    address bridger,
    address _wrsETH,
    uint256 _feeBps,
    address _rsETHOracle
) external initializer {
    UtilLib.checkNonZeroAddress(_wrsETH);      // checked
    UtilLib.checkNonZeroAddress(_rsETHOracle); // checked
    // admin and bridger are NOT checked
    _grantRole(DEFAULT_ADMIN_ROLE, admin);
    _setupRole(BRIDGER_ROLE, admin);
    _setupRole(BRIDGER_ROLE, bridger);
    ...
}
``` [1](#0-0) 

If `admin == address(0)`, OpenZeppelin's `AccessControl` grants `DEFAULT_ADMIN_ROLE` to `address(0)`. No real EOA or contract holds that role. Every function guarded by `onlyRole(DEFAULT_ADMIN_ROLE)` — including all five `reinitialize` overloads — becomes permanently uncallable. [2](#0-1) 

Fee ETH accumulates in `feeEarnedInETH` through every user `deposit()` call, but the withdrawal path requires admin authority. With no admin, that ETH is permanently locked.

### Impact Explanation
- **Permanent freezing of unclaimed yield (Medium):** `feeEarnedInETH` grows with every swap but can never be withdrawn once admin is lost.
- **No emergency pause:** The contract cannot be paused in response to an exploit, exposing all depositor ETH to ongoing risk.
- **No reconfiguration:** Oracle, fee BPS, daily mint limit, Stargate pool, and L1 vault address are all frozen at their initial (potentially incorrect) values with no upgrade path.

### Likelihood Explanation
Likelihood is low but non-negligible. The pattern is identical to the referenced audit finding: the risk materialises during redeployments on new L2 networks (Arbitrum, Optimism, Base, etc.) where deployment scripts may be adapted or run in a different environment. A single scripting error — passing `address(0)` for `admin` — produces a silently misconfigured contract that passes all on-chain checks at deploy time.

### Recommendation
Add zero-address guards for both `admin` and `bridger` in `initialize()`, mirroring the pattern already used for `_wrsETH` and `_rsETHOracle`:

```solidity
UtilLib.checkNonZeroAddress(admin);
UtilLib.checkNonZeroAddress(bridger);
``` [3](#0-2) 

### Proof of Concept
1. Deploy `RSETHPoolV2ExternalBridge` proxy and call `initialize(address(0), address(0), validWrsETH, feeBps, validOracle)`.
2. Deployment succeeds — no revert, no on-chain signal of misconfiguration.
3. Users call `deposit{value: 1 ether}(...)`. `feeEarnedInETH` grows; `wrsETH` is minted correctly.
4. Attempt to call any `reinitialize` or fee-withdrawal function → reverts with `AccessControl: account 0x000...000 is missing role DEFAULT_ADMIN_ROLE` for the caller.
5. `feeEarnedInETH` is permanently unrecoverable; the contract cannot be paused or reconfigured. [4](#0-3)

### Citations

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L186-229)
```text
    function reinitialize(address _l2Bridge, address _messenger)
        external
        reinitializer(5)
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        UtilLib.checkNonZeroAddress(_l2Bridge);
        UtilLib.checkNonZeroAddress(_messenger);

        l2Bridge = _l2Bridge;
        messenger = _messenger;

        emit L2BridgeSet(_l2Bridge);
        emit MessengerSet(_messenger);
    }

    /// @dev Reinitializer function to set the daily minting limit
    /// @param _dailyMintLimit The daily minting limit
    /// @param _startTimestamp The start timestamp for the daily minting limit
    function reinitialize(
        uint256 _dailyMintLimit,
        uint256 _startTimestamp
    )
        external
        reinitializer(4)
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

    /// @dev Reinitialize the contract
    /// @param _dstLzChainId The LayerZero ID for the ETH mainnet
    function reinitialize(uint32 _dstLzChainId) external reinitializer(3) onlyRole(DEFAULT_ADMIN_ROLE) {
        dstLzChainId = _dstLzChainId;
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

**File:** contracts/utils/UtilLib.sol (L11-13)
```text
    function checkNonZeroAddress(address address_) internal pure {
        if (address_ == address(0)) revert ZeroAddressNotAllowed();
    }
```
