### Title
Reentrancy via ERC-777 `tokensToSend` Hook in `initTransfer` Emits Unbacked `InitTransfer` Events — (File: `evm/src/omni-bridge/contracts/OmniBridge.sol`)

---

### Summary

`OmniBridge.initTransfer()` increments `currentOriginNonce` and then calls `IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount)`. For ERC-777 tokens, this triggers a `tokensToSend` hook on the sender **before** tokens are moved. An attacker controlling the sender address can re-enter `initTransfer` from this hook, obtain a fresh nonce, and emit a second `InitTransfer` event — while engineering the outer call's token transfer to silently no-op. NEAR treats every emitted `InitTransfer` event as proof of locked custody and will mint/release tokens on the destination chain for both events, producing unbacked wrapped supply.

---

### Finding Description

`initTransfer` in `OmniBridge.sol` follows this sequence for the plain-ERC-20 lock path:

```
currentOriginNonce += 1;                          // (1) nonce incremented
...
IERC20(tokenAddress).safeTransferFrom(            // (2) external call — ERC-777 fires
    msg.sender, address(this), amount             //     tokensToSend hook on attacker
);
...
emit BridgeTypes.InitTransfer(                    // (3) event emitted
    msg.sender, tokenAddress, currentOriginNonce, amount, ...
);
``` [1](#0-0) 

The nonce increment at step (1) is the only state mutation before the external call. This is documented as the "primary reentrancy defense" in `evm/CLAUDE.md`:

> *State before external calls: Always mutate state (e.g. mark nonce used) before any external call. This is the primary reentrancy defense.* [2](#0-1) 

However, this defense only prevents **same-nonce replay**. It does not prevent a re-entrant call from obtaining a **fresh nonce** and emitting a new, independently valid `InitTransfer` event.

There is no `ReentrancyGuard` or `nonReentrant` modifier anywhere in the EVM contracts.

ERC-777 tokens call `tokensToSend(operator, from, to, amount, ...)` on the registered hook of the **sender** before the balance update. An attacker who is both the `msg.sender` of `initTransfer` and the registered ERC-777 hook operator receives control mid-execution, after `currentOriginNonce` has been incremented but before tokens have moved.

---

### Impact Explanation

`InitTransfer` events are the **sole source of truth** for the NEAR side to credit inbound transfers:

> *The NEAR side reads this event (via light client or Wormhole) to complete the transfer. Every field needed to reconstruct the transfer must be in the event — it is the only data the NEAR side sees.* [3](#0-2) 

> *`InitTransfer` and `FinTransfer` events must contain every field needed to reconstruct the transfer.* [4](#0-3) 

If an attacker emits two `InitTransfer` events (nonces N and N+1) while only locking tokens once, NEAR will process both and mint/release double the tokens on the destination chain. This produces unbacked wrapped supply — a direct violation of the bridge's backing guarantee.

**Impact class**: High — duplicate cross-chain settlement producing double-credit / unbacked supply. Also qualifies as Critical — unauthorized creation of wrapped bridge assets without corresponding custody.

---

### Likelihood Explanation

- ERC-777 tokens exist in production (e.g., historical imBTC, various DeFi tokens). Any ERC-777 token that is or becomes registered on the bridge is an attack surface.
- The attacker needs no privileged role. `initTransfer` is a public, unpermissioned entry point callable by any address.
- `logMetadata` is permissionless, allowing an attacker to register a freshly deployed malicious ERC-777 token on NEAR and then exploit the reentrancy. [5](#0-4) 

---

### Recommendation

Add OpenZeppelin's `ReentrancyGuardUpgradeable` to `OmniBridge` and apply `nonReentrant` to both `initTransfer` and `initTransfer1155`. Alternatively, explicitly document that tokens with sender-side callbacks (ERC-777) are not supported and add a token allowlist enforced on-chain.

---

### Proof of Concept

**Setup**: Attacker deploys `MaliciousERC777` — an ERC-777 token whose `tokensToSend` hook re-enters `initTransfer` exactly once. The outer `safeTransferFrom` is engineered to succeed (return without reverting) without moving tokens.

**Execution**:

1. Attacker calls `bridge.initTransfer(maliciousToken, 100, 0, 0, "near:attacker.near", "")`.
2. `currentOriginNonce` → N. [6](#0-5) 
3. `safeTransferFrom(attacker, bridge, 100)` fires `tokensToSend` on attacker.
4. From hook: attacker calls `bridge.initTransfer(maliciousToken, 100, 0, 0, "near:attacker.near", "")` again.
   - `currentOriginNonce` → N+1.
   - Inner `safeTransferFrom` actually transfers 100 tokens to bridge.
   - `emit InitTransfer(attacker, maliciousToken, N+1, 100, ...)` — **legitimate, backed**.
5. Hook returns. Outer `safeTransferFrom` completes — token contract skips the balance update (returns success with no state change).
6. `emit InitTransfer(attacker, maliciousToken, N, 100, ...)` — **unbacked**.

**Result**: Bridge holds 100 tokens. NEAR sees two valid `InitTransfer` events (nonces N and N+1, each for 100 tokens) and mints 200 tokens worth of value on the destination chain. The attacker has created 100 tokens of unbacked wrapped supply. [7](#0-6) [8](#0-7)

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L224-232)
```text
    function logMetadata(address tokenAddress) external payable {
        string memory name = IERC20Metadata(tokenAddress).name();
        string memory symbol = IERC20Metadata(tokenAddress).symbol();
        uint8 decimals = IERC20Metadata(tokenAddress).decimals();

        logMetadataExtension(tokenAddress, name, symbol, decimals);

        emit BridgeTypes.LogMetadata(tokenAddress, name, symbol, decimals);
    }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L380-437)
```text
    ) external payable whenNotPaused(PAUSED_INIT_TRANSFER) {
        currentOriginNonce += 1;
        if (fee >= amount) {
            revert InvalidFee();
        }

        uint256 extensionValue;
        if (tokenAddress == address(0)) {
            if (fee != 0) {
                revert InvalidFee();
            }
            extensionValue = msg.value - amount - nativeFee;
        } else {
            extensionValue = msg.value - nativeFee;
            if (customMinters[tokenAddress] != address(0)) {
                IERC20(tokenAddress).safeTransferFrom(
                    msg.sender,
                    customMinters[tokenAddress],
                    amount
                );
                ICustomMinter(customMinters[tokenAddress]).burn(
                    tokenAddress,
                    amount
                );
            } else if (isBridgeToken[tokenAddress]) {
                BridgeToken(tokenAddress).burn(msg.sender, amount);
            } else {
                IERC20(tokenAddress).safeTransferFrom(
                    msg.sender,
                    address(this),
                    amount
                );
            }
        }

        initTransferExtension(
            msg.sender,
            tokenAddress,
            currentOriginNonce,
            amount,
            fee,
            nativeFee,
            recipient,
            message,
            extensionValue
        );

        emit BridgeTypes.InitTransfer(
            msg.sender,
            tokenAddress,
            currentOriginNonce,
            amount,
            fee,
            nativeFee,
            recipient,
            message
        );
    }
```

**File:** evm/CLAUDE.md (L23-23)
```markdown
**EVM → NEAR (initTransfer)**: User calls `initTransfer` which burns/locks tokens on EVM and emits `InitTransfer` with all transfer details (sender, token, amount, fee, nativeFee, recipient, message). In the Wormhole variant, a Wormhole message is also sent. The NEAR side reads this event (via light client or Wormhole) to complete the transfer. Every field needed to reconstruct the transfer must be in the event — it is the only data the NEAR side sees.
```

**File:** evm/CLAUDE.md (L33-33)
```markdown
- **Event completeness**: `InitTransfer` and `FinTransfer` events must contain every field needed to reconstruct the transfer. The NEAR side relies solely on these events — any missing or ambiguous field means lost funds or spoofable transfers. Fields must not be collapsible (e.g. two different transfers must never produce the same event data)
```

**File:** evm/CLAUDE.md (L34-34)
```markdown
- **State before external calls**: Always mutate state (e.g. mark nonce used) before any external call (token transfer, ETH send, custom minter). This is the primary reentrancy defense
```
