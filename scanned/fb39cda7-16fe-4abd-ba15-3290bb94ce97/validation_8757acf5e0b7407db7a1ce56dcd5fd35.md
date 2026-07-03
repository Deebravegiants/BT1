### Title
Missing Zero-Address Validation for `admin` and `bridger` in Pool Initializers Permanently Freezes Fees and Bridgeable Assets - (File: contracts/pools/RSETHPoolV3.sol)

---

### Summary

The `initialize` functions across all L2 pool contracts (`RSETHPoolV3`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) and `RsETHTokenWrapper` validate `_wrsETH` and `_rsETHOracle` against the zero address but silently accept `address(0)` for `admin` and `bridger`. If either is zero at deployment, the corresponding role is irrevocably granted to `address(0)`, permanently disabling all functions gated behind that role.

---

### Finding Description

In `RSETHPoolV3.initialize`, only `_wrsETH` and `_rsETHOracle` are checked:

```solidity
UtilLib.checkNonZeroAddress(_wrsETH);
UtilLib.checkNonZeroAddress(_rsETHOracle);
// admin and bridger are NOT checked
_grantRole(DEFAULT_ADMIN_ROLE, admin);
_setupRole(BRIDGER_ROLE, bridger);
``` [1](#0-0) 

The same pattern is repeated verbatim in:

- `RSETHPoolV2ExternalBridge.initialize` [2](#0-1) 
- `RSETHPoolV3ExternalBridge.initialize` [3](#0-2) 
- `RSETHPoolV3WithNativeChainBridge.initialize` [4](#0-3) 
- `RsETHTokenWrapper.initialize` (no checks at all for `admin`, `bridger`, or `_altRsETH`) [5](#0-4) 

**Scenario A — `bridger = address(0)`:**

`BRIDGER_ROLE` is granted to `address(0)`. The following functions require `BRIDGER_ROLE` and become permanently uncallable by any real address:

- `withdrawFees(address receiver)` — accumulated ETH fees are permanently locked. [6](#0-5) 
- `moveAssetsForBridging(uint256 amount)` — ETH deposited by users can never be forwarded to L1, breaking the L2→L1 bridging flow. [7](#0-6) 

**Scenario B — `admin = address(0)`:**

`DEFAULT_ADMIN_ROLE` is granted to `address(0)`. The following functions become permanently uncallable:

- `unpause()` — if the contract is ever paused, it can never be unpaused. [8](#0-7) 
- `setDailyMintLimit()`, `setFeeBps()`, `setRSETHOracle()`, `addSupportedToken()` — all management functions are bricked. [9](#0-8) 

`UtilLib.checkNonZeroAddress` is available and used elsewhere in the same codebase for exactly this purpose: [10](#0-9) 

---

### Impact Explanation

**Scenario A** (`bridger = address(0)`): All ETH fee revenue accumulated in the pool is permanently frozen — no address can ever call `withdrawFees`. Additionally, `moveAssetsForBridging` is permanently disabled, meaning ETH deposited by users accumulates in the pool contract and is never forwarded to the L1 vault. wrsETH is minted to users but the backing ETH never reaches EigenLayer, creating a permanent protocol-level accounting mismatch. This constitutes **permanent freezing of unclaimed yield** (fees) and **temporary/permanent freezing of deposited funds** (bridgeable ETH).

**Scenario B** (`admin = address(0)`): The contract becomes permanently unmanageable. If a `PAUSER_ROLE` holder pauses the contract (PAUSER_ROLE can be granted by anyone with DEFAULT_ADMIN_ROLE — but since that is address(0), it cannot be granted post-deploy), user funds are permanently frozen.

---

### Likelihood Explanation

Low. This requires a deployment-time mistake where `address(0)` is passed as `admin` or `bridger`. However, the protocol deploys multiple pool instances across many L2 chains (Arbitrum, Optimism, Base, etc.), increasing the cumulative probability of a misconfiguration. The absence of any guard means the error is silent — the transaction succeeds and the contract appears functional until the missing role is exercised.

---

### Recommendation

Add `UtilLib.checkNonZeroAddress` calls for `admin` and `bridger` in all pool `initialize` functions, mirroring the pattern already used for `_wrsETH` and `_rsETHOracle`:

```solidity
UtilLib.checkNonZeroAddress(admin);
UtilLib.checkNonZeroAddress(bridger);
UtilLib.checkNonZeroAddress(_wrsETH);
UtilLib.checkNonZeroAddress(_rsETHOracle);
```

Apply the same fix to `RsETHTokenWrapper.initialize` for all three parameters.

---

### Proof of Concept

1. Deploy `RSETHPoolV3` proxy and call `initialize(address(0), address(0), validWrsETH, feeBps, validOracle, true)`.
2. Transaction succeeds. `DEFAULT_ADMIN_ROLE` and `BRIDGER_ROLE` are both held by `address(0)`.
3. Users call `deposit()` — succeeds, wrsETH is minted, ETH accumulates in the pool.
4. Operator attempts `moveAssetsForBridging(amount)` — reverts with `AccessControl: account 0x...sender is missing role BRIDGER_ROLE`.
5. ETH is permanently stuck; fees are permanently frozen; no admin can fix the state or upgrade the contract.

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L218-226)
```text
        UtilLib.checkNonZeroAddress(_wrsETH);
        UtilLib.checkNonZeroAddress(_rsETHOracle);

        __ERC20_init("rsETH", "rsETH");
        __AccessControl_init();
        __ReentrancyGuard_init();

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);
```

**File:** contracts/pools/RSETHPoolV3.sol (L453-461)
```text
    function withdrawFees(address receiver) external nonReentrant onlyRole(BRIDGER_ROLE) {
        // withdraw fees in ETH
        uint256 amountToSendInETH = feeEarnedInETH;
        feeEarnedInETH = 0;
        (bool success,) = payable(receiver).call{ value: amountToSendInETH }("");
        if (!success) revert TransferFailed();

        emit FeesWithdrawn(amountToSendInETH);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L482-493)
```text
    function moveAssetsForBridging(uint256 amount) external nonReentrant onlyRole(BRIDGER_ROLE) {
        if (amount == 0) revert InvalidAmount();

        // withdraw up to ETH - fees
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();
        if (amount > ethBalanceMinusFees) revert InsufficientBalanceInPool();

        (bool success,) = msg.sender.call{ value: amount }("");
        if (!success) revert TransferFailed();

        emit AssetsMovedForBridging(amount);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L518-521)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
```

**File:** contracts/pools/RSETHPoolV3.sol (L598-601)
```text
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) whenPaused {
        paused = false;
        emit Unpaused(msg.sender);
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L268-276)
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L340-348)
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L255-263)
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
