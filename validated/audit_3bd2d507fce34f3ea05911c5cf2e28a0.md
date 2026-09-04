### Title
Any unprivileged EOA can permanently invalidate another user's `emporiumMessage` nonce via `cancelEmporiumMessage`, griefing/freezing queued Emporium operations - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`cancelEmporiumMessage` only checks that the caller can produce a signature recovering to `msg.sender` for an arbitrary `emporiumMessage` value, but never checks that `msg.sender` is the `signerAddress`/owner of that message. Since `usedMessages` is a single global mapping keyed only by the raw `emporiumMessage` integer, any attacker can observe a victim's pending `emporiumMessage` (visible in mempool calldata as part of `CircomData`) and pre-emptively mark it used with their own self-signed cancel signature, causing the victim's legitimately signed `runAction` call to revert with `UsedMessage()`.

### Finding Description
The broken equality: the set of `emporiumMessage` values a user has actually authorized-and-intends-to-cancel should equal the set an attacker can mark as `usedMessages[...] = true`. In practice these sets are unrelated because `cancelEmporiumMessage` binds the signature only to `msg.sender`, not to the specific `emporiumMessage`'s intended owner (`stack.signerAddress`): [1](#0-0) 

Any address can produce a valid EIP-712 signature over `EMPORIUM_CANCEL_TYPEHASH(message)` using its own private key for any `message` value it chooses (including one it merely observed being used by someone else), since `verified` only requires `recoveredAddress == msg.sender`: [2](#0-1) 

This writes directly into the same `usedMessages` mapping consulted by `verifyWallet`, which is keyed purely by `circomData.emporiumMessage` with no linkage to the `EmporiumStack.signerAddress` or any per-account namespace: [3](#0-2) [4](#0-3) 

Exploit flow: a victim's relayer submits `runAction` with a `CircomData.emporiumMessage = M` for an `EmporiumStack` with `signerAddress != address(0)`. An attacker observes `M` in the mempool, signs `EmporiumCancel(M)` with their own EOA key, and calls `cancelEmporiumMessage(M, v, r, s)` with higher gas/priority to front-run. This sets `usedMessages[M] = true` before the victim's transaction lands. When the victim's `runAction` executes, `verifyWallet` reverts with `UsedMessage()` at the very first check, before the wallet-signature verification against `stack.signerAddress` even runs.

None of the existing guards prevent this: `verifyWallet`'s signature check (lines 318-340) validates the `EmporiumStack` payload's signer but is never reached because the `usedMessages` check happens first and unconditionally; `cancelEmporiumMessage` has no relationship check to `stack.signerAddress` at all.

### Impact Explanation
This allows any unprivileged EOA to grief a specific victim's queued/pending Emporium action by nonce-squatting an observed `emporiumMessage`, causing their otherwise-valid, signed operation to permanently fail with `UsedMessage()`. The affected operation can never be resubmitted under that exact message id. This is a temporary freezing of a legitimate user's queued action/funds-in-flight rather than theft — the underlying token balances held by the user's smart wallet/Emporium session are not moved to the attacker, and the user can, in principle, generate a fresh `CircomData`/`EmporiumStack` with a new `emporiumMessage` and re-sign to release the same funds later. This matches the "High - temporary freezing of user funds" category rather than Critical, since no value is permanently unrecoverable through this path alone (the user's ability to re-sign a new message for the same underlying balance is not itself blocked by this function).

### Likelihood Explanation
The attack requires only observing a pending transaction's calldata (public mempool data) and paying gas to front-run with a self-signed cancel message — no special privileges, no proof generation, and no funds at risk for the attacker. It is trivially repeatable against any victim using `signerAddress != address(0)` Emporium flows, and costs the attacker only the gas of one `cancelEmporiumMessage` call plus front-running priority fees.

### Recommendation
Bind cancellation authority to the message's intended owner rather than an arbitrary caller. Store the `signerAddress` (or hash of the full `EmporiumStack`) alongside `emporiumMessage` when first used/reserved, or require `cancelEmporiumMessage` to verify that `recoveredAddress == <the signerAddress embedded/committed for that message>` rather than merely `== msg.sender`. Alternatively, namespace `usedMessages` per signer (e.g., `usedMessages[signerAddress][emporiumMessage]`) so an unrelated address cannot invalidate another account's nonce space.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, set up a victim `signerAddress` wallet and construct a valid `EmporiumStack` with `signerAddress = victim`, sign `EMPORIUM_SIGNATURE_TYPEHASH` over some `emporiumMessage = M` with the victim's key.
2. As `attacker` (a distinct EOA with no relation to `victim`), sign `EMPORIUM_CANCEL_TYPEHASH(M)` with the attacker's own key, and call `cancelEmporiumMessage(M, v, r, s)` from `attacker`.
3. Assert `usedMessages[M] == true` after step 2 (verify via a subsequent call reverting, since mapping is internal) — i.e., call `runAction` with the victim's properly constructed `CircomData{emporiumMessage: M, ...}` and assert it reverts with `UsedMessage()`, even though the victim's own `EmporiumStack` signature over `M` was never used or cancelled by the victim.
4. Assert this occurred purely from the attacker's own self-signed cancel call with no reference to the victim's `signerAddress`, demonstrating `recoveredAddress == msg.sender (attacker)` was the only check performed in `cancelEmporiumMessage`, breaking the equality that "only the message's rightful owner/signer can cancel/burn it."

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L306-316)
```text
        EmporiumStorageVars storage $ = _getEmporiumStorage();

        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;

        if (stack.signerAddress == address(0)) {
            return;
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L353-367)
```text
    function cancelEmporiumMessage(uint256 emporiumMessage, uint8 v, bytes32 r, bytes32 s) external {
        EmporiumStorageVars storage $ = _getEmporiumStorage();

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumStorage.sol (L8-11)
```text
    struct EmporiumStorageVars {
        IHinkalHelper _hinkalHelper; // Hinkal Helper may change implementation
        mapping(uint256 => bool) usedMessages;
    }
```
