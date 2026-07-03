### Title
Missing Pause Mechanism on `SonicChainNativeTokenBridge` and `bridgeTokens` Allows Irreversible Bridge Operations During Degraded Bridge State - (`contracts/bridges/SonicChainNativeTokenBridge.sol`)

---

### Summary

`SonicChainNativeTokenBridge` has no pause function, and `RSETHPoolV3WithNativeChainBridge.bridgeTokens` lacks a `whenNotPaused` guard. When the Sonic bridge enters a degraded state, the protocol has no on-chain mechanism to halt in-flight bridge operations: pausing the pool blocks deposits but does not block `bridgeTokens`, and the bridge contract itself cannot be paused at all.

---

### Finding Description

**`SonicChainNativeTokenBridge`** inherits only `AccessControl` and `ReentrancyGuard`. There is no `paused` state variable, no `pause()`/`unpause()` function, and no `whenNotPaused` modifier anywhere in the contract. [1](#0-0) 

**`RSETHPoolV3WithNativeChainBridge`** does define a full pause system (`paused` bool, `PAUSER_ROLE`, `whenNotPaused` modifier, `pause()`/`unpause()` functions): [2](#0-1) [3](#0-2) [4](#0-3) 

However, `bridgeTokens` — the function that triggers the actual cross-chain burn — carries only `nonReentrant`, `onlySupportedToken`, and `onlyRole(BRIDGER_ROLE)`. The `whenNotPaused` modifier is absent: [5](#0-4) 

The call chain is:

```
BRIDGER_ROLE → RSETHPoolV3WithNativeChainBridge.bridgeTokens()
  → token.safeIncreaseAllowance(bridge, amount)
  → SonicChainNativeTokenBridge.bridgeTokenToL1()
    → sonicBridge.withdraw(uid, originalToken, amount)   // burns L2 tokens
``` [6](#0-5) 

Once `sonicBridge.withdraw` executes, L2 tokens are burned and a claim is registered on L1. If the Sonic bridge is in a degraded state, the L1 claim may be unprocessable or indefinitely delayed — but the burn is irreversible.

---

### Impact Explanation

When the Sonic bridge is known to be degraded:
- Pausing the pool blocks new deposits but **does not block `bridgeTokens`**.
- There is no pause path on `SonicChainNativeTokenBridge` itself.
- The `BRIDGER_ROLE` (which may be an automated keeper) can still call `bridgeTokens`, causing tokens to be burned on L2 with no corresponding L1 delivery until the bridge recovers.
- The protocol fails to deliver the promised cross-chain transfer for all in-flight operations initiated during the degraded window.

Impact: **Low — contract fails to deliver promised returns** (delayed or unclaimable L1 delivery for bridged tokens).

---

### Likelihood Explanation

Sonic's native bridge is an external dependency. Bridge degradation events (congestion, contract pauses, upgrade windows) are realistic operational scenarios. The asymmetry — pool has pause, bridge does not, and `bridgeTokens` bypasses the pool pause — means the gap is reachable whenever the Sonic bridge experiences any disruption.

---

### Recommendation

1. Add `whenNotPaused` to `bridgeTokens` in `RSETHPoolV3WithNativeChainBridge` so that pausing the pool also halts bridging: [7](#0-6) 

2. Add a `Pausable` pattern to `SonicChainNativeTokenBridge` (a `paused` bool, `PAUSER_ROLE`, `pause()`/`unpause()`, and a `whenNotPaused` guard on `bridgeTokenToL1`) so the bridge itself can be independently halted without relying on the pool layer. [8](#0-7) 

---

### Proof of Concept

```solidity
// 1. Deploy mock degraded Sonic bridge: withdraw() succeeds (burns tokens)
//    but L1 claim is never processable.
// 2. Deploy SonicChainNativeTokenBridge with mock sonicBridge.
// 3. Deploy RSETHPoolV3WithNativeChainBridge, configure bridge.
// 4. Pause the pool: pool.pause() — succeeds.
// 5. Assert: pool.paused() == true.
// 6. Call pool.bridgeTokens(token, amount) as BRIDGER_ROLE.
//    → Succeeds despite pool being paused (no whenNotPaused on bridgeTokens).
// 7. Observe: L2 tokens burned, L1 claim undeliverable.
// 8. Assert: no pause() function exists on SonicChainNativeTokenBridge.
//    → Confirmed: no path to halt the bridge contract independently.
```

The absence of `whenNotPaused` on `bridgeTokens` is directly verifiable at lines 553–561 of `RSETHPoolV3WithNativeChainBridge.sol`, and the absence of any pause mechanism in `SonicChainNativeTokenBridge` is confirmed by the full contract (lines 1–186). [9](#0-8)

### Citations

**File:** contracts/bridges/SonicChainNativeTokenBridge.sol (L1-16)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.27;

import { SafeERC20, IERC20 } from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import { AccessControl } from "@openzeppelin/contracts/access/AccessControl.sol";
import { ReentrancyGuard } from "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import { IL2TokenBridge } from "contracts/interfaces/L2/IL2TokenBridge.sol";
import { ISonicBridge, ISonicTokenPairs } from "contracts/interfaces/L2/ISonicBridge.sol";
import { UtilLib } from "contracts/utils/UtilLib.sol";

/// @title SonicChainNativeTokenBridge
/// @notice Bridge contract for transferring tokens from Sonic to Ethereum using Sonic's native bridge
/// @dev This contract must have the same address as SonicBridgeReceiver on ETH mainnet
/// @dev Implements IL2TokenBridge interface for integration with RSETHPoolV3AutoBridgedTokens
contract SonicChainNativeTokenBridge is IL2TokenBridge, AccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;
```

**File:** contracts/bridges/SonicChainNativeTokenBridge.sol (L73-73)
```text
    function bridgeTokenToL1(address recipient, uint256 amount) external payable override nonReentrant {
```

**File:** contracts/bridges/SonicChainNativeTokenBridge.sol (L111-121)
```text
        token.safeIncreaseAllowance(address(sonicBridge), amount);

        // Initiate withdrawal on Sonic bridge
        // Note: Sonic gateway will only allow SonicBridgeReceiver to claim (same address as this contract)
        sonicBridge.withdraw(uid, originalToken, amount);

        // Verify tokens were transferred/burned
        uint256 balanceAfter = token.balanceOf(address(this));
        if (balanceBefore - balanceAfter != amount) {
            revert BridgeFailed();
        }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L51-51)
```text
    bool public paused;
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L83-86)
```text
    modifier whenNotPaused() {
        if (paused) revert ContractPaused();
        _;
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L553-577)
```text
    function bridgeTokens(
        address token,
        uint256 amount
    )
        external
        payable
        nonReentrant
        onlySupportedToken(token)
        onlyRole(BRIDGER_ROLE)
    {
        if (tokenBridge[token] == address(0)) revert MissingBridgeForToken();
        if (amount == 0) revert InvalidAmount();

        // bridge up to the token balance minus fees
        uint256 tokenBalanceMinusFees = getTokenBalanceMinusFees(token);
        if (amount > tokenBalanceMinusFees) revert InsufficientBalance();

        // Approve the required amount to the bridge
        IERC20(token).safeIncreaseAllowance(tokenBridge[token], amount);

        // Call the bridge contract to transfer the tokens
        IL2TokenBridge(tokenBridge[token]).bridgeTokenToL1{ value: msg.value }(l1VaultETHForL2Chain, amount);

        emit BridgedTokenToL1(token, l1VaultETHForL2Chain, amount);
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L666-675)
```text
    function pause() external onlyRole(PAUSER_ROLE) whenNotPaused {
        paused = true;
        emit Paused(msg.sender);
    }

    /// @dev Unpauses the pausable methods in the contract
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) whenPaused {
        paused = false;
        emit Unpaused(msg.sender);
    }
```
