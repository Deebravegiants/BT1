### Title
Emporium relay-fee payment silently no-ops when `signerAddress` has no deployed `HinkalWallet` code - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.payRelayFees` pays the relay's fee out of a user's smart-contract wallet by calling `IHinkalWallet(signerAddress).doSendToRelay(...)`. That interface function has a `void` return type, so Solidity does **not** insert the automatic `extcodesize` guard it inserts for calls with non-empty return values. If `signerAddress` is an address that recovers correctly from an ECDSA signature but has no `HinkalWallet` contract code deployed at it (i.e. a bare EOA), the low-level call trivially "succeeds" with empty return data, and the relay fee is never actually transferred — exactly the unchecked-return/void-call gotcha described in the external report.

### Finding Description
In `EmporiumUpgradeable.sol`:

```solidity
function sendToRelayFromWallet(
    address relay,
    address signerAddress,
    uint256 relayFee,
    address feeToken
) internal {
    if (relayFee > 0) {
        IHinkalWallet(signerAddress).doSendToRelay(
            relay,
            relayFee,
            feeToken
        );
    }
}
``` [1](#0-0) 

`doSendToRelay` is declared with no return value:
```solidity
function doSendToRelay(
    address relay,
    uint256 actualAmount,
    address erc20TokenAddress
) external;
``` [2](#0-1) 

`signerAddress` is only validated via ECDSA signature recovery in `verifyWallet` — there is no check that a `HinkalWallet` contract actually exists at that address:
```solidity
(address recoveredAddress, ECDSA.RecoverError err) = ECDSA.tryRecover(
    hashedMessage, stack.v, stack.r, stack.s
);
bool verified = err == ECDSA.RecoverError.NoError &&
    recoveredAddress == stack.signerAddress;
if (!verified) { revert InvalidSignature(); }
``` [3](#0-2) 

`payRelayFees` invokes `payRelay` → `sendToRelayFromWallet` whenever `signerAddress != address(0)` and a fee is due, without any post-call check that the relay's balance actually increased:
```solidity
function payRelay(
    address relay, address signerAddress, uint256 relayFee, address erc20TokenAddress
) internal {
    if (relay == address(0) || relayFee == 0) return;
    if (signerAddress == address(0)) {
        sendToRelay(relay, relayFee, erc20TokenAddress);
    } else {
        sendToRelayFromWallet(relay, signerAddress, relayFee, erc20TokenAddress);
    }
}
``` [4](#0-3) 

For any address with no deployed code, calling a `void`-return external function via a Solidity interface does not revert (unlike calls that expect a non-empty ABI-encoded return, such as `callHinkalWallet`, where the compiler auto-inserts an `extcodesize` check). Consequently, an attacker who signs `EmporiumStack` with an arbitrary private key whose corresponding address never had a `HinkalWallet` deployed can produce a fully valid signature, pass `verifyWallet`, and have `payRelayFees` "successfully" call `doSendToRelay` on that empty address — moving zero tokens to the relay while the transaction completes normally, `usedMessages[emporiumMessage]` is marked used, and no revert occurs anywhere in `runAction` (the balance-equality checks in `runAction` only compare the Emporium contract's own token balances before/after, not the wallet's or relay's balance, so this fee-skip is invisible to that accounting).

### Impact Explanation
This breaks the intended fee equality: the relay/protocol is supposed to receive `relayFee`/`flatFee` for servicing an Emporium transaction on behalf of a signer, but the fee payment silently no-ops, causing the relay to permanently lose the fee it was promised for that transaction, with no revert or on-chain signal that payment failed. This matches "High — theft or permanent freezing of protocol/relay fees."

### Likelihood Explanation
Any unprivileged actor who can produce an `EmporiumStack` signature (with any EOA private key they generate themselves, not requiring a real `HinkalWallet` deployment) and submit it through `Hinkal.transact` → `_externalTransact` → `EmporiumUpgradeable.runAction` can trigger this. No admin/owner/relayer privilege is required — the attacker only needs to sign their own message and set `signerAddress` to an address with no wallet contract deployed.

### Recommendation
- Verify that `signerAddress` has non-zero code size (`signerAddress.code.length > 0`) before treating it as a `HinkalWallet`, or require `doSendToRelay`/`callHinkalWallet` calls to return an explicit success marker that is checked by the caller.
- Alternatively, check the relay's/fee-token balance before and after `sendToRelayFromWallet` and revert if the expected fee was not actually transferred, mirroring the balance-diff pattern already used elsewhere in `runAction`.

### Proof of Concept
1. Attacker generates a fresh private key `k` (address `A`), never deploying a `HinkalWallet` at `A`.
2. Attacker builds `EmporiumStack{ signerAddress: A, ops: [...], maxFee, deadline }` and signs it with `k`, producing a valid `(v, r, s)` per `EMPORIUM_SIGNATURE_TYPEHASH`.
3. Attacker crafts `CircomData` with `feeStructure.flatFee > 0`, `feeStructure.feeToken` set, and a valid ZK proof for the corresponding public inputs (the fee amount is a public input independent of whether `A` is a contract).
4. Calls `Hinkal.transact(...)` → `_externalTransact` → `EmporiumUpgradeable.runAction`.
5. `verifyWallet` succeeds (valid signature to `A`). `payRelayFees` computes `relayFee = flatFee` and calls `payRelay` → `sendToRelayFromWallet` → `IHinkalWallet(A).doSendToRelay(relay, relayFee, feeToken)`.
6. Since `A` has no code, the call returns success with empty data (void function, no `extcodesize` guard), and execution continues normally; `runAction` completes, `usedMessages[emporiumMessage]` is set, and the transaction finalizes.
7. The relay that processed this transaction (expecting `flatFee` in `feeToken`) receives nothing — the fee is permanently lost.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L186-199)
```text
    function sendToRelayFromWallet(
        address relay,
        address signerAddress,
        uint256 relayFee,
        address feeToken
    ) internal {
        if (relayFee > 0) {
            IHinkalWallet(signerAddress).doSendToRelay(
                relay,
                relayFee,
                feeToken
            );
        }
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L262-282)
```text
    function payRelay(
        address relay,
        address signerAddress,
        uint256 relayFee,
        address erc20TokenAddress
    ) internal {
        if (relay == address(0) || relayFee == 0) {
            return;
        }

        if (signerAddress == address(0)) {
            sendToRelay(relay, relayFee, erc20TokenAddress);
        } else {
            sendToRelayFromWallet(
                relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
        }
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L330-340)
```text
        (address recoveredAddress, ECDSA.RecoverError err) = ECDSA.tryRecover(
            hashedMessage,
            stack.v,
            stack.r,
            stack.s
        );
        bool verified = err == ECDSA.RecoverError.NoError &&
            recoveredAddress == stack.signerAddress;
        if (!verified) {
            revert InvalidSignature();
        }
```

**File:** contracts/types/IHinkalWallet.sol (L11-15)
```text
    function doSendToRelay(
        address relay,
        uint256 actualAmount,
        address erc20TokenAddress
    ) external;
```
