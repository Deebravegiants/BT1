### Title
`cancelEmporiumMessage` lets any unrelated address permanently burn any victim's `emporiumMessage` id, freezing their signed Emporium action - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`cancelEmporiumMessage` verifies only that the EIP-712 `EmporiumCancel(message)` signature recovers to `msg.sender`, never checking it against the `stack.signerAddress` that actually owns the message. Any attacker can self-sign a cancellation for an arbitrary `message` id and mark it used in `$.usedMessages`, permanently blocking the legitimate signer's future `transact` call that references the same id.

### Finding Description
The equality that should hold is: `usedMessages[M]` may only be set to `true` by (a) a valid `verifyWallet` consumption authorised by `stack.signerAddress`'s EIP-712 signature over `EmporiumSignature(message=M, ops, maxFee, deadline)`, or (b) a cancellation authorised by that same `stack.signerAddress`. Instead, `cancelEmporiumMessage` checks only: [1](#0-0) 
`recoveredAddress == msg.sender`, with no comparison to any stored or supplied `signerAddress` for `M`. Since `M` is an arbitrary `uint256` chosen off-chain by the wallet/relay (used both as the circuit's `emporiumMessage` public signal and as the `EmporiumSignature` nonce, per `CircomDataBuilder.formInputNormal`/`formBasicInput` and `getSignedMessageHash`), an attacker who merely observes or predicts `M` (e.g., from a pending mempool `Hinkal.transact`, or a sequential/off-chain-issued id scheme) can call `cancelEmporiumMessage(M, v, r, s)` with a signature they generate themselves (any EOA can self-sign an `EmporiumCancel(M)` message; `recoveredAddress` will trivially equal `msg.sender`==attacker). This sets `$.usedMessages[M] = true` in `EmporiumStorage`: [2](#0-1) 
The victim's subsequent `transact` invoking `runAction` → `verifyWallet` for the same `circomData.emporiumMessage == M` then reverts via `UsedMessage()`: [3](#0-2) 
because the check-then-set on `usedMessages[M]` happens before any signature is even validated against `stack.signerAddress`. No later step recovers `M`; the mapping is a simple one-way boolean with no owner-scoped namespace, no reset path, and no way to distinguish "cancelled by the rightful signer" from "cancelled by an attacker." The `onlyAllowedRecipient` modifier on `runAction` and `performHinkalChecks`/proof verification in the caller do not protect `M` itself, since `cancelEmporiumMessage` is a standalone, unauthenticated-with-respect-to-signer entry point with no access-control tie to `stack.signerAddress`.

### Impact Explanation
This permanently freezes the victim's specific signed `EmporiumStack` operation (and any UTXO/wallet funds routed through it), since `M` can never be reused and there is no recovery mechanism — the signer must produce a brand-new `EmporiumStack` with a different message id, but the attacker can repeat the front-run indefinitely for any message id they can observe. This matches the "permanent freezing of user funds" Critical category, and is fully repeatable and cheap for the attacker (one self-signed transaction per targeted `M`), with no privileged role required.

### Likelihood Explanation
Preconditions are modest: the attacker only needs visibility into (or the ability to predict) the `emporiumMessage` id `M` before the victim's `transact` transaction is mined — plausible via mempool observation of a pending transaction, or if `M` follows any observable/off-chain-issued scheme (e.g., sequential per-wallet nonces). No funds, deposits, or special privileges are needed by the attacker; the exploit is a single front-run transaction consisting purely of a self-signed EIP-712 message and a call to `cancelEmporiumMessage`.

### Recommendation
Require `cancelEmporiumMessage` to take the `signerAddress` as an explicit parameter (or bind it into the signed payload, e.g. `EmporiumCancel(uint256 message, address signer)`), verify `recoveredAddress == signerAddress`, and only allow that recovered/declared signer (not `msg.sender`) to cancel `M`. Optionally namespace `usedMessages` by `(signerAddress, message)` to prevent any cross-signer collisions entirely.

### Proof of Concept
Foundry test outline:
1. Deploy `EmporiumUpgradeable`, initialize with owner/hinkalHelper.
2. Victim (`signer`) picks message id `M`, constructs an `EmporiumStack` with `signerAddress = signer`, signs `EmporiumSignature(M, ops, maxFee, deadline)` — do not submit yet.
3. Attacker (`unrelatedEOA`, distinct private key) signs `EmporiumCancel(M)` under its own key and calls `cancelEmporiumMessage(M, v, r, s)`.
4. Assert `verified` succeeds (`recoveredAddress == attacker == msg.sender`) and `_getEmporiumStorage().usedMessages[M] == true` (read via a test harness exposing the storage, or infer via subsequent revert).
5. Simulate victim's `runAction`/`transact` call with `circomData.emporiumMessage == M` and the previously-prepared signed `EmporiumStack`; assert it reverts with `UsedMessage()`.
6. Confirm no function exists to reset `usedMessages[M]` back to `false`, demonstrating permanent freezing.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L306-313)
```text
        EmporiumStorageVars storage $ = _getEmporiumStorage();

        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;

```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L356-367)
```text
        bytes32 hashedMessage = _hashTypedDataV4(
            keccak256(abi.encode(EMPORIUM_CANCEL_TYPEHASH, emporiumMessage))
        );

        (address recoveredAddress, ECDSA.RecoverError err) = ECDSA.tryRecover(hashedMessage, v, r, s);
        bool verified = err == ECDSA.RecoverError.NoError && recoveredAddress == msg.sender;
        if (!verified) {
            revert InvalidSignature();
        }

        $.usedMessages[emporiumMessage] = true;
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumStorage.sol (L6-11)
```text
contract EmporiumStorage {
    /// @custom:storage-location erc7201:hinkal.storage.Emporium
    struct EmporiumStorageVars {
        IHinkalHelper _hinkalHelper; // Hinkal Helper may change implementation
        mapping(uint256 => bool) usedMessages;
    }
```
