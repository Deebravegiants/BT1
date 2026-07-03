### Title
Missing Zero Address Validation for `admin` and `bridger` in Pool `initialize` Functions - (File: contracts/pools/RSETHPoolV2.sol, contracts/pools/RSETHPoolV2ExternalBridge.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolV2NBA.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol, contracts/agETH/AGETHPoolV3.sol, contracts/L2/RsETHTokenWrapper.sol)

---

### Summary

Multiple `initialize` functions across pool and wrapper contracts validate critical contract addresses (`_wrsETH`, `_rsETHOracle`) but omit zero address checks for the `admin` and `bridger` role parameters. If `admin` is set to `address(0)`, `DEFAULT_ADMIN_ROLE` is permanently assigned to the zero address, making the contract irrecoverably unmanageable.

---

### Finding Description

The following `initialize` functions accept `admin` (and `bridger`) as parameters and immediately grant `DEFAULT_ADMIN_ROLE` (and `BRIDGER_ROLE`) to them, but perform no zero address validation on those role parameters:

**`contracts/pools/RSETHPoolV2.sol`** [1](#0-0) 

**`contracts/pools/RSETHPoolV2ExternalBridge.sol`** [2](#0-1) 

**`contracts/pools/RSETHPoolV3ExternalBridge.sol`** [3](#0-2) 

**`contracts/pools/RSETHPoolV2NBA.sol`** [4](#0-3) 

**`contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`** [5](#0-4) 

**`contracts/agETH/AGETHPoolV3.sol`** [6](#0-5) 

**`contracts/L2/RsETHTokenWrapper.sol`** [7](#0-6) 

In every case, the pattern is:

```solidity
UtilLib.checkNonZeroAddress(_wrsETH);      // ✓ checked
UtilLib.checkNonZeroAddress(_rsETHOracle); // ✓ checked
// admin and bridger are NOT checked       // ✗ missing
_grantRole(DEFAULT_ADMIN_ROLE, admin);
_setupRole(BRIDGER_ROLE, admin);
_setupRole(BRIDGER_ROLE, bridger);
```

The project's own `UtilLib.checkNonZeroAddress` utility exists precisely for this purpose: [8](#0-7) 

Contrast with contracts that do it correctly — e.g., `KernelVaultETH.initialize` checks every address parameter including `_admin` and `_operator`: [9](#0-8) 

---

### Impact Explanation

If `admin = address(0)` is supplied at initialization:

- `DEFAULT_ADMIN_ROLE` is permanently granted to `address(0)`, which can never sign transactions.
- All `onlyRole(DEFAULT_ADMIN_ROLE)` functions become permanently inaccessible. In `RSETHPoolV2.sol` alone there are 8 such functions (fee withdrawal, oracle updates, token support changes, pause/unpause, bridging configuration, etc.).
- The contract can never be paused in response to an emergency, and fee/oracle parameters can never be corrected.
- For `RsETHTokenWrapper`, the `reinitialize` function (gated by `DEFAULT_ADMIN_ROLE`) can never be called, freezing the set of allowed tokens permanently.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.** The pool continues to operate but becomes permanently unmanageable; no user funds are directly stolen, but the protocol loses all ability to respond to bugs, update parameters, or pause the contract.

---

### Likelihood Explanation

Likelihood is low. The `initialize` function is called once by the deployer. A deployment script that accidentally passes `address(0)` for `admin` — e.g., from an unset environment variable or a misconfigured deployment — would trigger this. The risk is elevated by the fact that the same pattern is repeated across seven contracts, increasing the probability of at least one deployment error across the protocol's multi-chain deployments.

---

### Recommendation

Add `UtilLib.checkNonZeroAddress` calls for `admin` and `bridger` in every affected `initialize` function, consistent with the pattern already used in `KernelVaultETH`, `KernelReceiver`, `KernelMerkleDistributor`, and `L1Vault`:

```solidity
function initialize(
    address admin,
    address bridger,
    address _wrsETH,
    uint256 _feeBps,
    address _rsETHOracle
) external initializer {
    UtilLib.checkNonZeroAddress(admin);    // ADD
    UtilLib.checkNonZeroAddress(bridger);  // ADD
    UtilLib.checkNonZeroAddress(_wrsETH);
    UtilLib.checkNonZeroAddress(_rsETHOracle);
    // ...
}
```

Apply the same fix to `RsETHTokenWrapper.initialize` for both `admin` and `bridger`.

---

### Proof of Concept

1. Deploy `RSETHPoolV2` (or any of the affected contracts) via its proxy.
2. Call `initialize(address(0), someBridger, wrsETH, feeBps, oracle)`.
3. The call succeeds — no revert — because there is no zero address check on `admin`.
4. `DEFAULT_ADMIN_ROLE` is now held exclusively by `address(0)`.
5. Attempt to call any admin-gated function (e.g., `withdrawFeeEarnedInETH`, `pause`, `setFeeBps`): every call reverts with `AccessControl: account 0x000...000 is missing role`.
6. The contract is permanently unmanageable with no recovery path, since `initialize` is protected by `initializer` and cannot be called again.

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

**File:** contracts/utils/UtilLib.sol (L11-13)
```text
    function checkNonZeroAddress(address address_) internal pure {
        if (address_ == address(0)) revert ZeroAddressNotAllowed();
    }
```

**File:** contracts/KERNEL/KernelVaultETH.sol (L156-160)
```text
        UtilLib.checkNonZeroAddress(_admin);
        UtilLib.checkNonZeroAddress(_operator);
        UtilLib.checkNonZeroAddress(_kernel);
        UtilLib.checkNonZeroAddress(_kernelOftAdapter);
        UtilLib.checkNonZeroAddress(_receiver);
```
