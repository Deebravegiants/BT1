### Title
Missing Zero-Address Check for `admin` in `initialize()` Permanently Locks Governance - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
`RSETHPoolV3.initialize()` validates `_wrsETH` and `_rsETHOracle` but omits zero-address validation for the `admin` parameter. If `admin` is `address(0)`, `DEFAULT_ADMIN_ROLE` is permanently granted to the zero address, making all admin-gated governance functions permanently inaccessible and requiring contract redeployment.

### Finding Description
In `RSETHPoolV3.initialize()`, only `_wrsETH` and `_rsETHOracle` are validated via `UtilLib.checkNonZeroAddress`. The `admin` and `bridger` parameters receive no zero-address check before being passed to `_grantRole` / `_setupRole`. [1](#0-0) 

If `admin = address(0)` is supplied at initialization:

```solidity
_grantRole(DEFAULT_ADMIN_ROLE, admin);   // grants role to address(0)
_setupRole(BRIDGER_ROLE, bridger);
``` [2](#0-1) 

`DEFAULT_ADMIN_ROLE` is the role-admin for every other role in OpenZeppelin `AccessControl`. With it held only by `address(0)`:

- `unpause()` (requires `DEFAULT_ADMIN_ROLE`) is permanently uncallable. [3](#0-2) 
- `setDailyMintLimit()` (requires `DEFAULT_ADMIN_ROLE`) is permanently uncallable. [4](#0-3) 
- `setFeeBps()` (requires `DEFAULT_ADMIN_ROLE`) is permanently uncallable. [5](#0-4) 
- No account can ever be granted `TIMELOCK_ROLE`, so `setRSETHOracle()`, `addSupportedToken()`, `setIsEthDepositEnabled()`, and `setSupportedTokenOracle()` are all permanently inaccessible. [6](#0-5) 

The same pattern exists identically in `RSETHPoolV3ExternalBridge.initialize()`, `RSETHPoolV2ExternalBridge.initialize()`, and `RSETHPoolV3WithNativeChainBridge.initialize()`. [7](#0-6) [8](#0-7) [9](#0-8) 

### Impact Explanation
If `admin = address(0)` is passed at deployment, the contract is permanently misconfigured. No governance action (oracle update, daily limit change, fee change, new token addition) can ever be executed. The contract must be redeployed. This matches **Low — Contract fails to deliver promised returns, but doesn't lose value**: user deposits continue to function (the `deposit()` path does not require `DEFAULT_ADMIN_ROLE`), so no funds are directly lost, but the protocol cannot manage or upgrade the pool.

### Likelihood Explanation
Deployment scripts or proxy initialization calls that accidentally pass `address(0)` for `admin` — a realistic fat-finger or misconfiguration error — trigger this permanently. Because the `initializer` modifier prevents re-initialization, there is no recovery path short of redeployment. The same class of error is the subject of the referenced external report.

### Recommendation
Add explicit zero-address validation for `admin` (and `bridger`) at the top of every `initialize()` function, consistent with the pattern already applied to `_wrsETH` and `_rsETHOracle`:

```solidity
function initialize(
    address admin,
    address bridger,
    address _wrsETH,
    uint256 _feeBps,
    address _rsETHOracle,
    bool _isEthDepositEnabled
) external initializer {
+   UtilLib.checkNonZeroAddress(admin);
+   UtilLib.checkNonZeroAddress(bridger);
    UtilLib.checkNonZeroAddress(_wrsETH);
    UtilLib.checkNonZeroAddress(_rsETHOracle);
    ...
}
```

Apply the same fix to `RSETHPoolV3ExternalBridge`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, and `RSETHPool`.

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import {RSETHPoolV3} from "contracts/pools/RSETHPoolV3.sol";
import {ERC1967Proxy} from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

contract MissingAdminCheckPoC is Test {
    RSETHPoolV3 pool;

    function test_zeroAdminLocksGovernance() public {
        RSETHPoolV3 impl = new RSETHPoolV3();
        address wrsETH   = makeAddr("wrsETH");
        address oracle   = makeAddr("oracle");
        address bridger  = makeAddr("bridger");

        // Mock oracle.getRate() so initialize doesn't revert on oracle call
        vm.mockCall(oracle, abi.encodeWithSignature("getRate()"), abi.encode(1 ether));

        bytes memory initData = abi.encodeCall(
            RSETHPoolV3.initialize,
            (address(0), bridger, wrsETH, 10, oracle, true) // admin = address(0)
        );
        ERC1967Proxy proxy = new ERC1967Proxy(address(impl), initData);
        pool = RSETHPoolV3(payable(address(proxy)));

        // DEFAULT_ADMIN_ROLE is held only by address(0)
        assertTrue(pool.hasRole(pool.DEFAULT_ADMIN_ROLE(), address(0)));
        assertFalse(pool.hasRole(pool.DEFAULT_ADMIN_ROLE(), address(this)));

        // setDailyMintLimit permanently inaccessible
        vm.expectRevert();
        pool.setDailyMintLimit(1000 ether);

        // unpause permanently inaccessible — contract must be redeployed
        vm.expectRevert();
        pool.unpause();
    }
}
```

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

**File:** contracts/pools/RSETHPoolV3.sol (L518-521)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
```

**File:** contracts/pools/RSETHPoolV3.sol (L533-537)
```text
    function setRSETHOracle(address _rsETHOracle) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(_rsETHOracle);
        rsETHOracle = _rsETHOracle;
        emit OracleSet(_rsETHOracle);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L598-601)
```text
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) whenPaused {
        paused = false;
        emit Unpaused(msg.sender);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L605-611)
```text
    function setDailyMintLimit(uint256 _dailyMintLimit) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_dailyMintLimit == 0) {
            revert InvalidDailyMintLimit();
        }
        dailyMintLimit = _dailyMintLimit;
        emit DailyMintLimitSet(_dailyMintLimit);
    }
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
