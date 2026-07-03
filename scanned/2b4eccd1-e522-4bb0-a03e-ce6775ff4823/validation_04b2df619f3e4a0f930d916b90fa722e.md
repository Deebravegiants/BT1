### Title
Missing Zero-Address Validation for `admin` and `bridger` in `initialize` - (File: `contracts/pools/RSETHPoolV2.sol`)

### Summary
Multiple pool `initialize` functions validate token and oracle addresses for zero but omit equivalent checks on the `admin` and `bridger` role parameters. If either is supplied as `address(0)`, the corresponding role is permanently granted to the zero address, making all role-gated functions inaccessible and — in the worst case — permanently trapping user ETH in the contract.

### Finding Description
`RSETHPoolV2.initialize` (and the same pattern in `RSETHPoolV2ExternalBridge`, `RSETHPoolV2NBA`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPool`, `AGETHPoolV3`, `RsETHTokenWrapper`, and `AGETHTokenWrapper`) calls `UtilLib.checkNonZeroAddress` on the token/oracle addresses but performs no such check on `admin` or `bridger`:

```solidity
// contracts/pools/RSETHPoolV2.sol  L186-L193
function initialize(address admin, address bridger, address _wrsETH, uint256 _feeBps, address _rsETHOracle)
    external initializer
{
    UtilLib.checkNonZeroAddress(_wrsETH);      // ✓ checked
    UtilLib.checkNonZeroAddress(_rsETHOracle); // ✓ checked
    // admin and bridger are NOT checked       // ✗ missing
    ...
    _grantRole(DEFAULT_ADMIN_ROLE, admin);
    _setupRole(BRIDGER_ROLE, admin);
    _setupRole(BRIDGER_ROLE, bridger);
    ...
}
```

`UtilLib.checkNonZeroAddress` is a one-liner that reverts on `address(0)`:

```solidity
// contracts/utils/UtilLib.sol  L11-L13
function checkNonZeroAddress(address address_) internal pure {
    if (address_ == address(0)) revert ZeroAddressNotAllowed();
}
```

Consequences by scenario:

| Scenario | Effect |
|---|---|
| `admin = address(0)` | `DEFAULT_ADMIN_ROLE` → `address(0)`. `unpause()`, all `reinitialize()` overloads, and role-grant calls are permanently inaccessible. |
| `bridger = address(0)` (admin also zero) | `BRIDGER_ROLE` → `address(0)` only. `withdrawFees()` and `bridgeAssets()` are permanently inaccessible; deposited ETH can never leave the contract. |

### Impact Explanation
**Medium — Temporary/Permanent freezing of funds.**

If both `admin` and `bridger` are zero, every ETH deposit made by users via `deposit()` accumulates in the contract with no path to `bridgeAssets()` (requires `BRIDGER_ROLE`) or `withdrawFees()` (requires `BRIDGER_ROLE`). The ETH is permanently locked. Even with only `admin = address(0)`, the contract can never be upgraded via `reinitialize()` overloads (all gated on `DEFAULT_ADMIN_ROLE`), and `unpause()` is permanently inaccessible, meaning any future pause would freeze funds with no recovery path.

### Likelihood Explanation
Deployment misconfiguration (e.g., scripting error, copy-paste of a zero placeholder) is a realistic operational risk, especially given that the codebase already applies `UtilLib.checkNonZeroAddress` to every other address parameter in the same initializers. The asymmetry — oracle/token addresses are guarded, role addresses are not — makes an accidental zero slip-through plausible.

### Recommendation
Add `UtilLib.checkNonZeroAddress` for `admin` and `bridger` (or equivalent role address) at the top of every affected `initialize` function, mirroring the pattern already used in `L1Vault.initialize`, `KernelVaultETH.initialize`, and `RSETHPoolNoWrapper.initialize`:

```solidity
UtilLib.checkNonZeroAddress(admin);
UtilLib.checkNonZeroAddress(bridger);
UtilLib.checkNonZeroAddress(_wrsETH);
UtilLib.checkNonZeroAddress(_rsETHOracle);
```

### Proof of Concept

1. Deploy `RSETHPoolV2` behind a proxy.
2. Call `initialize(address(0), address(0), validWrsETH, feeBps, validOracle)`.
3. Transaction succeeds — no revert.
4. `DEFAULT_ADMIN_ROLE` and `BRIDGER_ROLE` are both held only by `address(0)`.
5. Any user calls `deposit{value: 1 ether}("ref")` — succeeds, ETH enters the contract.
6. Attempt `withdrawFees(receiver)` or `bridgeAssets()` — reverts with `AccessControl: account 0x... is missing role BRIDGER_ROLE`.
7. Attempt `unpause()` — reverts with `AccessControl: account 0x... is missing role DEFAULT_ADMIN_ROLE`.
8. ETH is permanently locked with no privileged path to recover it.

**Affected locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/pools/RSETHPoolV2.sol (L176-198)
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

**File:** contracts/pools/RSETHPool.sol (L222-251)
```text
    function initialize(
        address admin,
        address manager,
        address _rsETH,
        address _wstETH,
        uint256 _feeBps,
        address _rsETHOracle,
        address _wstETH_ETHOracle
    )
        external
        initializer
    {
        UtilLib.checkNonZeroAddress(_rsETH);
        UtilLib.checkNonZeroAddress(_wstETH);

        __ERC20_init("rsETH", "rsETH");
        __AccessControl_init();
        __ReentrancyGuard_init();

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        // legacy settings
        _setupRole(LEGACY_MANAGER_ROLE, admin);
        _setupRole(LEGACY_MANAGER_ROLE, manager);

        wrsETH = IERC20Upgradeable(_rsETH);
        legacyWstETH = IERC20Upgradeable(_wstETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
        legacyWstETH_ETHOracle = _wstETH_ETHOracle;
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

**File:** contracts/L2/RsETHTokenWrapper.sol (L55-64)
```text
    function initialize(address admin, address bridger, address _altRsETH) external initializer {
        __ERC20_init("rsETHWrapper", "wrsETH");
        __ERC20Permit_init("rsETHWrapper");
        __AccessControl_init();

        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);

        _addAllowedToken(_altRsETH);
    }
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L45-55)
```text
    function initialize(address admin, address manager, address _altAgETH) external initializer {
        __ERC20_init("agETHWrapper", "agETH");
        __ERC20Permit_init("agETHWrapper");
        __AccessControl_init();

        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(MANAGER_ROLE, manager);
        _setupRole(BRIDGER_ROLE, manager);

        allowedTokens[_altAgETH] = true;
    }
```

**File:** contracts/utils/UtilLib.sol (L11-13)
```text
    function checkNonZeroAddress(address address_) internal pure {
        if (address_ == address(0)) revert ZeroAddressNotAllowed();
    }
```
