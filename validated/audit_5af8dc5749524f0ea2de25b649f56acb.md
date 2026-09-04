## Title
Global (non-namespaced) `usedMessages` mapping in `cancelEmporiumMessage` lets any attacker permanently freeze another signer's queued Emporium operation - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

## Summary
`cancelEmporiumMessage` only verifies that a signature recovers to `msg.sender`, but it never ties `msg.sender` to the intended signer of that particular `emporiumMessage` id. Because `usedMessages` is a single global `mapping(uint256 => bool)` keyed only by the raw `emporiumMessage` integer [1](#0-0) , any unprivileged attacker can sign `EmporiumCancel(emporiumMessage)` with their own throwaway key and burn a message id that a different, legitimate signer intends to use later, permanently blocking that signer's `runAction` call.

## Finding Description
The broken equality: "the party who cancels message id `X`" should equal "the party who is entitled to use message id `X`" (i.e. the signer who will later present `X` inside `circomData.emporiumMessage` in a `runAction` call). Instead, the code only enforces "the party who cancels message id `X`" == "whoever produced a valid signature over `EmporiumCancel(X)` for their own address" - with zero binding to any specific intended signer.

Code path:
- `cancelEmporiumMessage(uint256 emporiumMessage, uint8 v, bytes32 r, bytes32 s)` hashes `EMPORIUM_CANCEL_TYPEHASH` over just `emporiumMessage`, recovers the signer, and checks only `recoveredAddress == msg.sender` [2](#0-1) .
- It then sets `$.usedMessages[emporiumMessage] = true` unconditionally - this is the exact same global mapping consulted by `verifyWallet` during `runAction`: `if ($.usedMessages[circomData.emporiumMessage]) revert UsedMessage();` [3](#0-2) .
- Since anyone can produce a valid `EmporiumCancel(X)` signature for their own address for *any* `X` (attackers control their own private key and can sign anything), and the mapping has no per-signer namespace, an attacker only needs to know or guess a real signer's intended `emporiumMessage` value to permanently mark it used before the real signer's transaction lands.
- `emporiumMessage` is a plain `uint256` field of `CircomData`, populated off-chain (see `contracts/CircomDataBuilder.sol`) and passed as plaintext calldata to `runAction`; it is not cryptographically derived from or bound to the intended `signerAddress` in `verifyWallet`'s `EMPORIUM_SIGNATURE_TYPEHASH` hash beyond being one of the signed fields for the *actual operation* signature - but nothing stops a third party from separately signing and submitting a *cancel* for that same integer value with their own key, since `EMPORIUM_CANCEL_TYPEHASH` carries no signer-specific salt.
- The doc comment on the function ("via a fresh signature recovering to msg.sender (so no one else can cancel it for them)") reflects a mistaken security assumption: it prevents someone from impersonating the *victim's address* to cancel, but does not prevent an unrelated third party from cancelling the same numeric id under their own identity, because the id space is shared/global rather than scoped per-signer (e.g., `usedMessages[keccak256(abi.encode(signerAddress, emporiumMessage))]`).

Existing guards checked and found insufficient:
- `verifyWallet`'s check `$.usedMessages[circomData.emporiumMessage]` uses the exact same unscoped mapping, so it cannot distinguish a legitimate cancellation from a griefing one [4](#0-3) .
- The `EMPORIUM_SIGNATURE_TYPEHASH` used for real operations does bind `stack.signerAddress` implicitly via the ECDSA recovery for `runAction`, but this has no bearing on the separate `cancelEmporiumMessage` flow, which is a completely independent code path with independent authorization logic.

## Impact Explanation
An attacker can, without any privileged role, permanently freeze a legitimate signer's queued Emporium operation for a chosen (or observed/guessed) `emporiumMessage` value by front-running `cancelEmporiumMessage` with their own signature. After this, the legitimate signer's correctly-signed `runAction` call for that message id will always revert with `UsedMessage()` [5](#0-4) . This is a permanent freezing of a signer's queued off-chain-authorized action (and any funds/UTXO outputs routed through that specific Emporium call), matching the "temporary/permanent freezing of user funds" / "executing calls or moving assets... never authorised"-adjacent High severity category. The attack is repeatable for every guessed/observed message id and costs the attacker only gas plus generating a trivial ECDSA signature over their own address.

## Likelihood Explanation
Feasibility depends on the attacker being able to learn or predict the `emporiumMessage` value a target signer intends to use before it lands on-chain. Given `emporiumMessage` is described as "simple integers/nonces chosen off-chain," and is transmitted in plaintext as part of `CircomData` in the `runAction` transaction (mempool-visible), an attacker monitoring the mempool for pending `EmporiumUpgradeable.runAction` calls can extract `circomData.emporiumMessage` and front-run with `cancelEmporiumMessage` using their own key before the original transaction is mined. This requires no special role, no compromised keys, and no interaction with out-of-scope areas (verifiers, circuits). It is a straightforward, low-cost front-running attack enabled purely by the on-chain authorization logic gap.

## Recommendation
Scope `usedMessages` per intended signer rather than as a single global namespace, e.g. change the mapping key to `keccak256(abi.encode(signerAddress, emporiumMessage))` (or `mapping(address => mapping(uint256 => bool))`), and require `cancelEmporiumMessage` to take an explicit `signerAddress` parameter that must equal `recoveredAddress` (the caller cancelling their own message), while `verifyWallet` should look up `usedMessages[stack.signerAddress][circomData.emporiumMessage]`. This ensures only the actual intended signer (or someone in possession of that signer's key) can mark that signer's message id as used/cancelled.

## Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable` (proxy) with a legitimate signer key (`victimPk`) and an attacker key (`attackerPk`), both unprivileged EOAs.
2. Have the victim decide off-chain to use `emporiumMessage = 42` for a future `runAction` call, and construct/sign the corresponding `EMPORIUM_SIGNATURE_TYPEHASH` payload (`ops`, `maxFee`, `deadline`) with `victimPk`. Do not yet submit it.
3. As the attacker, sign `EMPORIUM_CANCEL_TYPEHASH` over `message = 42` with `attackerPk`, and call `cancelEmporiumMessage(42, v, r, s)` from `attacker` address. Assert this succeeds and `usedMessages[42] == true` (verify via a subsequent call or storage read/event, or by triggering the downstream revert in step 4).
4. Submit the victim's originally prepared `runAction` call (via `HinkalWallet`/relay path with correct `circomData.emporiumMessage = 42` and valid `stack.v/r/s` signed by `victimPk`), and assert it reverts with `UsedMessage()`.
5. Assert the equality break: before step 3, `usedMessages[42] == false` and victim's call would have succeeded (test independently on a fresh id with no attacker interference); after step 3, `usedMessages[42] == true` set entirely by an unrelated attacker key, causing an otherwise valid, correctly-signed victim transaction to permanently fail.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumStorage.sol (L8-11)
```text
    struct EmporiumStorageVars {
        IHinkalHelper _hinkalHelper; // Hinkal Helper may change implementation
        mapping(uint256 => bool) usedMessages;
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L306-313)
```text
        EmporiumStorageVars storage $ = _getEmporiumStorage();

        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;

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
