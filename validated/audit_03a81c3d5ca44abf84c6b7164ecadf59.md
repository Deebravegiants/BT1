### Title
Unprotected Public `initialize()` in `OmniBridgeWormhole` Allows Front-Running to Seize Admin Control — (`evm/src/omni-bridge/contracts/OmniBridge.sol` / `OmniBridgeWormhole.sol`)

---

### Summary

`OmniBridge.initialize()` is declared `public initializer`. `OmniBridgeWormhole` inherits it and adds its own `initializeWormhole()` (also `initializer`) that calls `initialize()` internally. Because `initialize()` is `public`, any unprivileged actor can call it directly on a freshly deployed proxy before the legitimate deployer calls `initializeWormhole()`. Doing so consumes the single-use `initializer` slot, permanently blocks `initializeWormhole()`, and grants the attacker `DEFAULT_ADMIN_ROLE` and `PAUSABLE_ADMIN_ROLE` over the bridge.

---

### Finding Description

`OmniBridge` exposes two reachable initialization entry points on any `OmniBridgeWormhole` proxy:

**Entry point 1 — intended path:** [1](#0-0) 

`initializeWormhole()` is marked `initializer` and internally calls `initialize()`.

**Entry point 2 — unintended public path:** [2](#0-1) 

`initialize()` is `public initializer`. On a fresh proxy (`_initialized == 0`), it is callable by anyone. It grants `DEFAULT_ADMIN_ROLE` and `PAUSABLE_ADMIN_ROLE` to `_msgSender()`.

The implementation contract is protected by `_disableInitializers()` in the constructor: [3](#0-2) 

However, this only protects the implementation address itself. The proxy's storage starts with `_initialized == 0` and is fully open until initialization is called.

**Attack sequence:**

1. Deployer broadcasts a transaction to deploy the `OmniBridgeWormhole` proxy (without atomic initialization).
2. Attacker observes the pending transaction in the mempool and front-runs with a call to `OmniBridge.initialize(anyAddr, anyAddr, anyChainId)` on the new proxy.
3. OZ `initializer` modifier sets `_initialized = 1`. Attacker receives `DEFAULT_ADMIN_ROLE` and `PAUSABLE_ADMIN_ROLE`.
4. Deployer's subsequent call to `initializeWormhole()` reverts — `_initialized >= 1` blocks it permanently.
5. `_wormhole` is never set, but the attacker holds full admin control.

---

### Impact Explanation

With `DEFAULT_ADMIN_ROLE`, the attacker can:

- Call `setNearBridgeDerivedAddress()` to substitute their own signing key: [4](#0-3) 

- With a controlled `nearBridgeDerivedAddress`, forge valid ECDSA signatures accepted by `finTransfer()`, minting arbitrary amounts of any bridge token to any recipient: [5](#0-4) 

- Call `upgradeToken()` to replace bridge token implementations: [6](#0-5) 

- Call `_authorizeUpgrade()` (UUPS) to replace the bridge implementation itself: [7](#0-6) 

This constitutes **Critical** impact: unauthorized minting of wrapped bridge assets and full custody escape through a forged `finTransfer` settlement path.

---

### Likelihood Explanation

The attack requires only that the proxy deployment and `initializeWormhole()` call are not in the same transaction. This is a realistic deployment pattern (separate deploy + init transactions). A mempool-watching bot can reliably detect and front-run the uninitialized proxy. No privileged access, leaked keys, or social engineering is required — the attacker is strictly unprivileged and enters through the public `initialize()` function.

---

### Recommendation

1. **Change `OmniBridge.initialize()` visibility from `public` to `internal`** so it can only be called from within `initializeWormhole()` (or equivalent subclass initializers), not directly by external callers.

2. **Alternatively**, deploy and initialize the proxy atomically using the constructor's `data` parameter of `ERC1967Proxy`, passing the `initializeWormhole` calldata, so no window exists between deployment and initialization.

3. Ensure all future proxy deployments use `new ERC1967Proxy(impl, abi.encodeCall(initializeWormhole, (...)))` in a single transaction.

---

### Proof of Concept

```solidity
// 1. Deployer broadcasts proxy deployment (not yet initialized)
address proxy = address(new ERC1967Proxy(wormholeImpl, ""));

// 2. Attacker front-runs before initializeWormhole() is called:
OmniBridge(proxy).initialize(
    address(0xdead),   // tokenImplementationAddress (arbitrary)
    address(attacker), // nearBridgeDerivedAddress — attacker's signing key
    1                  // omniBridgeChainId
);
// Attacker now holds DEFAULT_ADMIN_ROLE and PAUSABLE_ADMIN_ROLE.
// _initialized == 1; initializeWormhole() is permanently blocked.

// 3. Attacker signs a finTransfer payload with their key:
//    nearBridgeDerivedAddress == attacker's EOA
//    ECDSA.recover(hash, attackerSig) == nearBridgeDerivedAddress ✓
// => finTransfer mints arbitrary bridge tokens to attacker.
```

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridgeWormhole.sol (L32-46)
```text
    function initializeWormhole(
        address tokenImplementationAddress,
        address nearBridgeDerivedAddress,
        uint8 omniBridgeChainId,
        address wormholeAddress,
        uint8 consistencyLevel
    ) external initializer {
        initialize(
            tokenImplementationAddress,
            nearBridgeDerivedAddress,
            omniBridgeChainId
        );
        _wormhole = IWormhole(wormholeAddress);
        _consistencyLevel = consistencyLevel;
    }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L67-70)
```text
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L72-86)
```text
    function initialize(
        address tokenImplementationAddress_,
        address nearBridgeDerivedAddress_,
        uint8 omniBridgeChainId_
    ) public initializer {
        tokenImplementationAddress = tokenImplementationAddress_;
        nearBridgeDerivedAddress = nearBridgeDerivedAddress_;
        omniBridgeChainId = omniBridgeChainId_;

        __UUPSUpgradeable_init();
        __AccessControl_init();
        __Pausable_init_unchained();
        _grantRole(DEFAULT_ADMIN_ROLE, _msgSender());
        _grantRole(PAUSABLE_ADMIN_ROLE, _msgSender());
    }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L279-313)
```text
    function finTransfer(
        bytes calldata signatureData,
        BridgeTypes.TransferMessagePayload calldata payload
    ) external payable whenNotPaused(PAUSED_FIN_TRANSFER) {
        if (completedTransfers[payload.destinationNonce]) {
            revert NonceAlreadyUsed(payload.destinationNonce);
        }

        completedTransfers[payload.destinationNonce] = true;

        bytes memory borshEncoded = bytes.concat(
            bytes1(uint8(BridgeTypes.PayloadType.TransferMessage)),
            Borsh.encodeUint64(payload.destinationNonce),
            bytes1(payload.originChain),
            Borsh.encodeUint64(payload.originNonce),
            bytes1(omniBridgeChainId),
            Borsh.encodeAddress(payload.tokenAddress),
            Borsh.encodeUint128(payload.amount),
            bytes1(omniBridgeChainId),
            Borsh.encodeAddress(payload.recipient),
            bytes(payload.feeRecipient).length == 0 // None or Some(String) in rust
                ? bytes("\x00")
                : bytes.concat(
                    bytes("\x01"),
                    Borsh.encodeString(payload.feeRecipient)
                ),
            bytes(payload.message).length == 0
                ? bytes("")
                : Borsh.encodeBytes(payload.message)
        );
        bytes32 hashed = keccak256(borshEncoded);

        if (ECDSA.recover(hashed, signatureData) != nearBridgeDerivedAddress) {
            revert InvalidSignature();
        }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L559-566)
```text
    function upgradeToken(
        address tokenAddress,
        address implementation
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(isBridgeToken[tokenAddress], "ERR_NOT_BRIDGE_TOKEN");
        BridgeToken proxy = BridgeToken(tokenAddress);
        proxy.upgradeToAndCall(implementation, bytes(""));
    }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L568-572)
```text
    function setNearBridgeDerivedAddress(
        address nearBridgeDerivedAddress_
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        nearBridgeDerivedAddress = nearBridgeDerivedAddress_;
    }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L594-596)
```text
    function _authorizeUpgrade(
        address newImplementation
    ) internal override onlyRole(DEFAULT_ADMIN_ROLE) {}
```
