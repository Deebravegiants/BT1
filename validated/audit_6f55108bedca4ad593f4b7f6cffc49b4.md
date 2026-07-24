### Title
Attacker-Controlled `message` Field Selects 3-Arg `mint` Path, Permanently Redirecting Bridged Tokens to `_systemAddress` on HyperLiquid — (`File: evm/src/omni-bridge/contracts/HlBridgeToken.sol`)

---

### Summary

`OmniBridge.finTransfer` dispatches to one of two different `mint` overloads on `IBridgeToken` depending solely on whether `payload.message` is empty. For `HlBridgeToken`, the 3-arg overload has a materially different side-effect: it immediately transfers all freshly minted tokens from the recipient to `_systemAddress`. Because `message` is an attacker-supplied field that flows from `initTransfer` through the MPC signature into `finTransfer`, any unprivileged user can force the 3-arg path and permanently redirect another user's bridged tokens.

---

### Finding Description

**Two calling conventions, two behaviors — the Gnosis analog**

In `OmniBridge.finTransfer`, the bridge selects between two `IBridgeToken.mint` overloads based on `payload.message.length`:

```solidity
// OmniBridge.sol lines 337-349
} else if (isBridgeToken[payload.tokenAddress]) {
    if (payload.message.length == 0) {
        IBridgeToken(payload.tokenAddress).mint(
            payload.recipient,
            payload.amount
        );
    } else {
        IBridgeToken(payload.tokenAddress).mint(
            payload.recipient,
            payload.amount,
            payload.message   // ← 3-arg path
        );
    }
}
``` [1](#0-0) 

For the base `BridgeToken`, both overloads are functionally identical — both call `_mint(account, value)` and return: [2](#0-1) 

`HlBridgeToken` overrides the 3-arg `mint` with a critically different body:

```solidity
// HlBridgeToken.sol lines 76-83
function mint(
    address account,
    uint256 value,
    bytes memory
) external override onlyOwner {
    _mint(account, value);
    _update(account, _systemAddress, value);  // ← transfers ALL tokens away
}
``` [3](#0-2) 

`_update(account, _systemAddress, value)` is an ERC-20 internal transfer that moves `value` tokens **from** `account` **to** `_systemAddress`. The net effect: the recipient is minted `value` tokens and immediately has all of them taken away. The 2-arg path (inherited from `BridgeToken`) does not call `_update` and leaves tokens with the recipient.

**The `message` field is fully attacker-controlled**

`initTransfer` accepts `message` as a plain `string calldata` with no validation:

```solidity
// OmniBridge.sol lines 373-380
function initTransfer(
    address tokenAddress,
    uint128 amount,
    uint128 fee,
    uint128 nativeFee,
    string calldata recipient,
    string calldata message          // ← caller supplies freely
) external payable whenNotPaused(PAUSED_INIT_TRANSFER) {
``` [4](#0-3) 

The `message` field is included verbatim in the `InitTransfer` event and in the Borsh-encoded payload that the MPC signs. The MPC signs whatever the event contains; it does not validate or reject non-empty messages. In `finTransfer`, the signed `message` is decoded from `TransferMessagePayload.message`: [5](#0-4) 

and the branch condition `payload.message.length == 0` is the sole gate between the safe 2-arg path and the destructive 3-arg path.

---

### Impact Explanation

When the 3-arg `mint` fires on an `HlBridgeToken`:

1. `_mint(recipient, amount)` — recipient's balance increases by `amount`.
2. `_update(recipient, _systemAddress, amount)` — recipient's balance decreases by `amount`; `_systemAddress` balance increases by `amount`.

The recipient ends with zero tokens. The bridge nonce (`destinationNonce`) is marked used before the mint call: [6](#0-5) 

so the transfer is permanently consumed and cannot be replayed. Tokens are irreversibly redirected to `_systemAddress` (the HyperLiquid system address), which is not under the recipient's control. This constitutes an **irreversible fund lock / permanent loss** for the recipient.

---

### Likelihood Explanation

- The attacker needs only to call `initTransfer` on any source chain with `message` set to any non-empty byte string (e.g., `"x"`).
- No privileged access, no key compromise, no colluding MPC signers required.
- The MPC will sign the payload as-is; the relayer will submit `finTransfer`; the branch fires automatically.
- Any `HlBridgeToken`-backed asset on HyperLiquid EVM is affected whenever a transfer carries a non-empty message.
- The attacker can target any victim's incoming transfer by front-running the `initTransfer` on the source chain with their own transfer to the same recipient, or simply by being the sender themselves and losing their own funds — but more critically, a malicious sender can grief any recipient by including a non-empty message in a transfer directed at them.

---

### Recommendation

**Short term:** In `OmniBridge.finTransfer`, always call the 2-arg `mint` for `isBridgeToken` tokens, passing `payload.message` through a separate, explicit hook if token-specific message handling is needed — do not use the presence of `message` to select between overloads with different token-transfer side-effects.

**Long term:** `HlBridgeToken.mint(address, uint256, bytes)` should not silently redirect tokens to `_systemAddress` when called from the bridge's `finTransfer` path. The 3-arg overload is designed for the HyperCore minting path (`coreReceiveWithData`), not for cross-chain settlement. Either remove the `_update` call from the 3-arg `mint` and introduce a separate `mintToCore` function, or gate the `_update` call on the caller being the system address rather than the owner.

---

### Proof of Concept

1. Attacker calls `initTransfer(hlToken, amount, fee, 0, "near:victim.near", "x")` on the source chain. `message = "x"` (one byte, non-empty).
2. MPC observes `InitTransfer` event, Borsh-encodes the payload including `message = "x"`, signs it.
3. Relayer calls `finTransfer(sig, payload)` on HyperLiquid EVM where `payload.message = "x"`.
4. `finTransfer` executes:
   - `completedTransfers[nonce] = true` — nonce consumed.
   - `isBridgeToken[hlToken]` is true, `customMinters[hlToken]` is zero.
   - `payload.message.length == 1 != 0` → calls `IBridgeToken(hlToken).mint(victim, amount, "x")`.
5. `HlBridgeToken.mint` executes:
   - `_mint(victim, amount)` — victim balance = `amount`.
   - `_update(victim, _systemAddress, amount)` — victim balance = 0, `_systemAddress` balance += `amount`.
6. Victim receives 0 tokens. Nonce is spent. Funds are permanently in `_systemAddress`.

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L283-287)
```text
        if (completedTransfers[payload.destinationNonce]) {
            revert NonceAlreadyUsed(payload.destinationNonce);
        }

        completedTransfers[payload.destinationNonce] = true;
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L337-349)
```text
        } else if (isBridgeToken[payload.tokenAddress]) {
            if (payload.message.length == 0) {
                IBridgeToken(payload.tokenAddress).mint(
                    payload.recipient,
                    payload.amount
                );
            } else {
                IBridgeToken(payload.tokenAddress).mint(
                    payload.recipient,
                    payload.amount,
                    payload.message
                );
            }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L373-380)
```text
    function initTransfer(
        address tokenAddress,
        uint128 amount,
        uint128 fee,
        uint128 nativeFee,
        string calldata recipient,
        string calldata message
    ) external payable whenNotPaused(PAUSED_INIT_TRANSFER) {
```

**File:** evm/src/omni-bridge/contracts/BridgeToken.sol (L50-60)
```text
    function mint(address beneficiary, uint256 amount) external onlyOwner {
        _mint(beneficiary, amount);
    }

    function mint(
        address account,
        uint256 value,
        bytes memory
    ) external virtual onlyOwner {
        _mint(account, value);
    }
```

**File:** evm/src/omni-bridge/contracts/HlBridgeToken.sol (L76-83)
```text
    function mint(
        address account,
        uint256 value,
        bytes memory
    ) external override onlyOwner {
        _mint(account, value);
        _update(account, _systemAddress, value);
    }
```

**File:** evm/src/omni-bridge/contracts/BridgeTypes.sol (L5-14)
```text
    struct TransferMessagePayload {
        uint64 destinationNonce;
        uint8 originChain;
        uint64 originNonce;
        address tokenAddress;
        uint128 amount;
        address recipient;
        string feeRecipient;
        bytes message;
    }
```
