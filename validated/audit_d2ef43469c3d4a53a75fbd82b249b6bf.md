### Title
Relay fee silently skipped via wallet-mode Emporium calls to a non-contract `signerAddress` - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.verifyWallet` only checks that `stack.signerAddress` recovers correctly from an ECDSA signature; it never verifies that `signerAddress` is actually a deployed `HinkalWallet` contract. `payRelayFees` then unconditionally routes the relay-fee payment through `IHinkalWallet(signerAddress).doSendToRelay(...)` whenever `signerAddress != address(0)`. A user can set `signerAddress` to a plain EOA they control (signing the EIP-712 message with that EOA's own key), which makes `verifyWallet` pass, while the subsequent external call to a codeless address becomes a silent EVM no-op that returns success without transferring any tokens.

### Finding Description
`verifyWallet` ( [1](#0-0) ) recovers `recoveredAddress` from `(stack.v, stack.r, stack.s)` and only requires `recoveredAddress == stack.signerAddress`. Nothing constrains `signerAddress` to be a contract implementing `IHinkalWallet`, e.g. via an `extcodesize` check, a registry/factory lookup, or `IERC165`/`supportsInterface` probing — despite `HinkalWallet.supportsInterface` existing precisely for such checks ( [2](#0-1) ).

Later, `payRelayFees` computes the fee owed to the relay and, whenever `signerAddress != address(0)`, calls `sendToRelayFromWallet`, which performs `IHinkalWallet(signerAddress).doSendToRelay(relay, relayFee, feeToken)` with no success/return check beyond normal Solidity call semantics: [3](#0-2) [4](#0-3) 

Because a normal external call (a plain `CALL` under the hood) to an address with no bytecode succeeds trivially in the EVM (no revert, empty return data, no state change), calling `doSendToRelay` on an EOA is a silent no-op: `success` is effectively `true` with no tokens moved. Since `doSendToRelay` on a real `HinkalWallet` returns nothing, the caller has no way to detect that no code executed. This breaks the balance equality the relay-fee mechanism is supposed to enforce — the relayer should receive `relayFee`, but receives nothing — and this discrepancy is never cross-checked against the Emporium balance-delta invariant in `runAction` ( [5](#0-4) ), because the wallet-mode fee transfer happens outside the contract and is not reflected in `balancesBefore`/`balancesAfter` for the Emporium contract itself.

### Impact Explanation
This allows any user going through the "stateful"/wallet-authorized Emporium path to set `signerAddress` to an arbitrary EOA under their own control, sign honestly with that EOA's key (satisfying `verifyWallet`), and thereby have `relayFee`/`flatFee` computed and "charged" against `deltaAmountChanges` accounting but never actually transferred to the relay. This is a permanent loss of protocol/relay fees, which the report's impact rubric classifies as High ("theft or permanent freezing of protocol/relay fees").

### Likelihood Explanation
The attacker only needs to control a normal EOA and produce a valid EIP-712 signature for it (trivial), and needs a valid ZK proof authorizing the underlying shielded operation, which any legitimate shielded-pool user already possesses. No relayer/admin collusion or privileged key is required, only the attacker's own signing key for their own transaction — this is squarely an unprivileged-EOA path.

### Recommendation
In `verifyWallet` (or `runAction` before invoking wallet-mode fee/operation calls), assert that `signerAddress` has nonzero code size (or otherwise verify it's a registered/expected `HinkalWallet`, e.g. via `IERC165(signerAddress).supportsInterface(type(IHinkalWallet).interfaceId)`) before trusting calls such as `doSendToRelay`/`callHinkalWallet` to have any effect. Alternatively, have `payRelayFees`/`sendToRelayFromWallet` verify a genuine balance change on the fee token/relay side after the call, mirroring the `BalanceChangeShouldBePositive` check already used for the main Emporium balances.

### Proof of Concept
1. Attacker generates a valid Hinkal shielded proof/CircomData for an Emporium action with `feeStructure.flatFee > 0` (or `variableRate` fee) and a nonzero `relay`.
2. Attacker builds an `EmporiumStack` with `signerAddress = attackerEOA` (a plain wallet address with no deployed contract code), fills `ops` with any stateless call not requiring `invokeWallet` (or an empty/no-op op), sets `maxFee`/`deadline` accordingly.
3. Attacker signs the EIP-712 `EMPORIUM_SIGNATURE_TYPEHASH` payload with `attackerEOA`'s private key, producing `(v, r, s)` that recover to `attackerEOA`.
4. Calls into `EmporiumUpgradeable.runAction` via the normal Hinkal flow; `verifyWallet` succeeds because `recoveredAddress == stack.signerAddress == attackerEOA`.
5. `payRelayFees` computes `relayFee`/`flatFee` and calls `IHinkalWallet(attackerEOA).doSendToRelay(relay, relayFee, feeToken)`. Since `attackerEOA` has no code, this call returns success without transferring any tokens.
6. Transaction completes successfully; the relay never receives its fee, while all other accounting (Emporium's own balance-delta check) passes because the fee transfer was never routed through Emporium's own balance in the first place.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-145)
```text
        payRelayFees(circomData, stack.signerAddress, deltaAmountChanges);

        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        UTXO[] memory utxoSet = new UTXO[](
            circomData.erc20TokenAddresses.length
        );

        uint256 utxoSetLength;

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L219-260)
```text
            if (isFeeToken) {
                foundToken = true;
            }

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

**File:** contracts/external-actions/emporium/HinkalWallet.sol (L60-68)
```text
    // EIP-165: Supports the following interfaces: IERC721Receiver, IERC1155Receiver, IERC165, IERC1271
    function supportsInterface(
        bytes4 _interfaceId
    ) public view virtual override(Transferer) returns (bool) {
        return
            super.supportsInterface(_interfaceId) ||
            _interfaceId == type(IERC165).interfaceId ||
            _interfaceId == type(IERC1271).interfaceId;
    }
```
