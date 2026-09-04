### Title
Emporium relay fee can be silently skipped by pointing `signerAddress` at an attacker-controlled EOA - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction()` lets a user route a Hinkal transaction through a `HinkalWallet` by supplying an `EmporiumStack` with a `signerAddress` and an ECDSA signature over the stack. Nothing in the code verifies that `signerAddress` is actually a deployed `HinkalWallet` contract bound to this Emporium — it only checks that the ECDSA signature recovers to `signerAddress`. An attacker can therefore set `signerAddress` to a fresh EOA they control (trivially producing a valid self-signature), which causes the wallet-side relay-fee transfer to be silently skipped while the transaction still completes successfully.

### Finding Description
`verifyWallet()` only validates the ECDSA signature against `stack.signerAddress`; it never checks that this address is a contract, let alone a genuine `HinkalWallet` instance pointing back at this `Emporium`: [1](#0-0) 

When `stack.signerAddress != address(0)`, relay fees are paid from that address via `sendToRelayFromWallet` → `IHinkalWallet(signerAddress).doSendToRelay(...)`: [2](#0-1) [3](#0-2) 

`doSendToRelay` has a `void` return type: [4](#0-3) 

Because the callee's return type is `void`, Solidity does not insert the implicit `extcodesize` check it uses for calls whose return data must be ABI-decoded. Calling a `void` external function on an address with no code (an EOA) executes a plain `CALL` that always "succeeds" without doing anything. If the attacker sets `signerAddress` to an EOA they hold the private key for (any freshly generated keypair works — the signature check in `verifyWallet` only needs `ECDSA.tryRecover` to return that same address, which any self-signed message trivially satisfies), the call to `doSendToRelay` silently no-ops: no ERC20/ETH transfer happens, but `payRelay`/`payRelayFees` return normally as if the fee had been paid.

This breaks the equality the fee mechanism is supposed to enforce: the relay is promised `feeStructure.flatFee` in exchange for submitting/relaying the transaction, but the actual value transfer that is supposed to realize that promise never happens, and nothing downstream (in particular the balance-diff equality check in `Hinkal.transact`, which only checks `circomData.erc20TokenAddresses` balances of the Hinkal contract itself) catches the missing relay-side transfer, since that transfer is expected to originate from the (bogus) wallet address, not from Hinkal's own balance.

Contrast this with `callHinkalWallet`, which returns `(bool, bytes)` — a non-void type — so Solidity does apply the `extcodesize` guard there and calls to an EOA correctly revert. Only the fee-payment path (`doSendToRelay`) is affected because of its `void` signature.

### Impact Explanation
This lets any unprivileged user route their own shielded transaction through the Emporium external action while promising (off-chain) a relay a `feeStructure.flatFee`/fee-token payment, but never actually deliver it, since the wallet-side transfer is a silent no-op. This is theft of protocol/relay fees — the relay expends gas and bandwidth executing the transaction under the on-chain fee-payment guarantee, but receives nothing. This matches the "High — theft ... of protocol/relay fees" impact category.

### Likelihood Explanation
Likelihood is high for any unprivileged actor: generating an EOA and self-signing the `EmporiumStack` typed-data message requires no special privilege, no admin/relay/manager role, and no assumption about a compromised key — it only requires reusing a key the attacker already controls as `signerAddress`. The only prerequisite is using the wallet-fee-payment code path (`signerAddress != address(0)`) with `feeStructure.flatFee > 0`.

### Recommendation
In `verifyWallet` (or before invoking any `IHinkalWallet(signerAddress)` call), assert that `signerAddress` is a contract and specifically a `HinkalWallet` deployed for this `Emporium`, e.g. require `signerAddress.code.length > 0` and `HinkalWallet(payable(signerAddress)).emporium() == address(this)` (or use a registry mapping populated at wallet-deployment time). Alternatively, change `doSendToRelay` to return a value (e.g. `bool`) so Solidity's implicit `extcodesize` check applies uniformly to all `IHinkalWallet` calls, and/or explicitly check `signerAddress.code.length > 0` before any external call is made to it.

### Proof of Concept
1. Attacker generates a fresh keypair `(pk, EOA)`, with no relation to any deployed `HinkalWallet`.
2. Attacker builds a valid ZK proof for their own shielded UTXOs (no special privilege needed) and constructs `CircomData` routing through the Emporium `externalActionId`, with `feeStructure.flatFee > 0` and a `relay` set.
3. Attacker builds `EmporiumStack{ signerAddress: EOA, ops: [...], maxFee, deadline }`, computes the EIP-712 digest per `EMPORIUM_SIGNATURE_TYPEHASH`, and signs it with `pk` — `ECDSA.tryRecover` in `verifyWallet` will recover `EOA`, matching `stack.signerAddress`, so the check passes.
4. `runAction` executes; `payRelayFees` → `payRelay` → `sendToRelayFromWallet` → `IHinkalWallet(EOA).doSendToRelay(relay, flatFee, feeToken)` is called on the plain EOA. Because `doSendToRelay` is `void`, no `extcodesize` guard applies, and the call is a silent no-op that returns success.
5. The relay never receives `flatFee`, yet the transaction completes and passes all downstream checks in `Hinkal.transact`, since those only validate the Hinkal contract's own token balance diffs, not the relay's receipt of fees.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L222-260)
```text

            uint256 relayFee = 0;
            uint256 flatFee = isFeeToken ? feeStructure.flatFee : 0;

            if (signerAddress == address(0)) {
                uint256 sumAbs = uint256(-deltaAmountChanges[i]);

                EmporiumStorageVars storage $ = _getEmporiumStorage();
                relayFee = $._hinkalHelper.calculateRelayFee(
                    sumAbs,
                    flatFee,
                    feeStructure.variableRate
                );
            } else {
                relayFee = flatFee;
            }

            payRelay(
                circomData.relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
        }

        if (!foundToken && feeStructure.flatFee != 0) {
            require(
                signerAddress != address(0),
                "Gas Token in Emporium is not found"
            );

            payRelay(
                circomData.relay,
                signerAddress,
                feeStructure.flatFee,
                feeStructure.feeToken
            );
        }
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-340)
```text
    function verifyWallet(
        EmporiumStack memory stack,
        CircomData calldata circomData
    ) internal {
        EmporiumStorageVars storage $ = _getEmporiumStorage();

        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;

        if (stack.signerAddress == address(0)) {
            return;
        }

        bytes32 hashedMessage = _hashTypedDataV4(
            keccak256(
                abi.encode(
                    EMPORIUM_SIGNATURE_TYPEHASH,
                    circomData.emporiumMessage,
                    _hashEmporiumOps(stack.ops),
                    stack.maxFee,
                    stack.deadline
                )
            )
        );

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
