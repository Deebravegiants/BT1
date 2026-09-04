## Finding [1](#0-0) 

### Title
Relay fee and wallet-op execution can be silently skipped via an uncontracted `signerAddress` in `EmporiumUpgradeable.runAction` - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction` trusts `stack.signerAddress`, a value fully controlled by the calling user (decoded from `circomData.externalActionData.externalActionMetadata`), to be a deployed `HinkalWallet` contract. The only validation performed is an ECDSA signature check that `signerAddress` matches the recovered signer of the EIP-712 message — a check any attacker can pass trivially by setting `signerAddress` to an EOA they control and signing with their own key.

### Finding Description
`verifyWallet` only checks that a valid ECDSA signature recovers to `stack.signerAddress`; it never verifies that `signerAddress` is a genuine `HinkalWallet` contract deployed by the protocol. [2](#0-1) 

Because `signerAddress` can be an EOA with no contract code, every call made against it via `IHinkalWallet(signerAddress)` — both the wallet stateful op-execution (`callHinkalWallet`) and the fee-payment call (`doSendToRelay`) — is a low-level `call` to an address with no code. In the EVM/Solidity, such calls always return `success == true` with empty returndata, without executing anything: [3](#0-2) [4](#0-3) 

`payRelayFees`/`payRelay` route the relay fee through `sendToRelayFromWallet` whenever `signerAddress != address(0)`, instead of paying it out of Emporium's own token balance: [5](#0-4) 

Since this call never actually transfers tokens (target has no code), the relay fee is never paid, yet `success` is `true`, so `runAction` proceeds to completion without reverting. The end-of-function balance-consistency check (`balanceChange < 0` revert) only compares Emporium's own token balances before/after — it never sees the wallet-side balance and therefore cannot catch a fee that should have come from the wallet but never moved. [6](#0-5) 

This is the same root-cause class as the multisig report: a privileged contract sends an arbitrary message to an address it never validates as the intended, code-bearing counterparty, letting the caller shape the target so the "action" becomes a no-op while the surrounding logic still treats it as successfully executed.

### Impact Explanation
The relay (or protocol) that services the transaction is entitled to its `flatFee`/`variableRate` fee whenever `signerAddress != address(0)`. By picking an EOA they control as `signerAddress`, an attacker can complete an Emporium `runAction` execution (including any "invokeWallet" ops that they choose to make into no-ops) while permanently denying the relay its fee. This is a direct **theft of protocol/relay fees**, falling under the High-impact bucket ("theft or permanent freezing of protocol/relay fees").

### Likelihood Explanation
The attack requires no privileged role — any user submitting a Hinkal `transact` call that routes through the Emporium external action can construct `EmporiumStack.signerAddress` themselves and sign it with an ordinary EOA key they own. No wallet-factory registration or on-chain existence check gates this value, so the attack is straightforward and repeatable for every Emporium call with `signerAddress != address(0)`.

### Recommendation
- In `verifyWallet` (or before it), require that `signerAddress` has non-zero code size (or is the address predicted/registered by an authoritative `HinkalWallet` factory) before trusting it as a wallet.
- Alternatively, when `signerAddress != address(0)`, verify post-call that `success` was accompanied by an expected state change (e.g., check the fee token's balance movement out of `signerAddress`, or require `extcodesize(signerAddress) > 0`) rather than trusting the raw `call` success flag.

### Proof of Concept
1. Attacker deposits into the shielded pool and prepares an Emporium `transact` call with `circomData.externalActionData.externalActionId` pointing at Emporium and `externalActionMetadata` encoding an `EmporiumStack` where:
   - `signerAddress = attackerEOA` (an address the attacker fully controls, no contract code deployed there).
   - `ops` contains at least one `invokeWallet = true` op (irrelevant content — it becomes a no-op).
   - `v, r, s` = a valid EIP-712 signature over the stack, signed by `attackerEOA`'s private key — trivially producible since the attacker owns the key.
   - `feeStructure.flatFee > 0`, `circomData.relay != address(0)`.
2. `Hinkal.transact` verifies the proof/calldata hash (both succeed, since `signerAddress` and the signature are just data fields hashed into `calldataHash`/the proof, with no requirement that `signerAddress` be a contract) and calls `EmporiumUpgradeable.runAction`.
3. `verifyWallet` passes because the signature recovers to `attackerEOA` (`stack.signerAddress`).
4. The `invokeWallet` op calls `IHinkalWallet(attackerEOA).callHinkalWallet(...)` — a call to an address with no code — which returns `success = true` and does nothing.
5. `payRelayFees` → `payRelay` → `sendToRelayFromWallet` calls `IHinkalWallet(attackerEOA).doSendToRelay(...)`, again a no-code call that trivially succeeds without moving any tokens to the relay.
6. `runAction` completes without reverting; the relay receives no fee even though the transaction is reported as successfully processed.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-120)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external override onlyAllowedRecipient returns (UTXO[] memory) {
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );

        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        verifyWallet(stack, circomData);

        for (uint256 i = 0; i < stack.ops.length; i++) {
            EmporiumOperation memory op = stack.ops[i];

            bool success;
            bytes memory err;

            // CASE 1: Stateful Interaction
            if (op.invokeWallet && stack.signerAddress != address(0)) {
                (success, err) = IHinkalWallet(stack.signerAddress)
                    .callHinkalWallet(op.endpoint, op.callData, op.value);
            }
            // CASE 2: Stateless Interaction
            else {
                bytes4 selector = bytes4(op.callData);
                if (
                    selector == IHinkalWallet.callHinkalWallet.selector ||
                    selector == IHinkalWallet.doSendToRelay.selector
                ) {
                    revert UnauthorizedWalletCall();
                }

                (success, err) = op.endpoint.call{value: op.value}(op.callData);
            }

            if (!success) {
                revert CallFailed(err);
            }
        }

        payRelayFees(circomData, stack.signerAddress, deltaAmountChanges);
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L132-151)
```text
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 balanceChange = int256(balancesAfter[i]) -
                int256(balancesBefore[i]);

            if (deltaAmountChanges[i] < 0) {
                balanceChange -= deltaAmountChanges[i];
                // this equation reads: total change of emporium balance = what was moved to emporium (-deltaAmountChange) + how emporium balance changed through tx (balanceChange)
            }

            // the only case when balanceChange can be < 0, when there were some funds on emporium before the call
            if (balanceChange < 0) {
                revert BalanceChangeShouldBePositive();
            }

            UTXO memory utxoOut = handleOut(balanceChange, circomData, i);

            if (utxoOut.amount > 0) {
                utxoSet[utxoSetLength++] = utxoOut;
            }
        }
```

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-341)
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
