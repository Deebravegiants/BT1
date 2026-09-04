### Title
Emporium `verifyWallet` never binds `erc20TokenAddresses`/`amountChanges`/`stealthAddressStructure` into the owner's signature, letting anyone who obtains a valid unspent `EmporiumStack` front-run it and redirect the resulting wallet funds to their own shielded UTXO - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.verifyWallet` recovers a signature only over `EMPORIUM_SIGNATURE_TYPEHASH(message, opsHash, maxFee, deadline)`, so the owner authorizes *which calls run* but not *who benefits from the resulting token balance change*. Any unprivileged actor who obtains a signed, not-yet-consumed `EmporiumStack` (e.g. observed in the mempool, shared for relaying, etc.) can submit it via `Hinkal.transact` with a self-generated proof whose `circomData.erc20TokenAddresses`, `amountChanges`, `outCommitments` and `stealthAddressStructure` are entirely their own, causing any real ERC20 value that the signed `ops` move out of the victim's wallet/`HinkalWallet` to be credited as a brand-new shielded UTXO to the attacker instead of the signer.

### Finding Description
Equality broken: **(who is authorized to be paid for the executed `ops`) as constrained by the owner's EIP-712 signature over `EMPORIUM_SIGNATURE_TYPEHASH`** != **(who actually receives the resulting UTXO / token credit)** as determined at runtime by `circomData.erc20TokenAddresses`, `deltaAmountChanges`/`amountChanges`, `circomData.outCommitments` and `circomData.stealthAddressStructure`, none of which appear in the signed hash: [1](#0-0) 

`verifyWallet` only checks `usedMessages`, the EIP-712 hash of `(emporiumMessage, opsHash, maxFee, deadline)`, `deadline`, and `feeStructure.flatFee <= maxFee`: [2](#0-1) 

`ops` itself is bound (endpoint/invokeWallet/value/callData are hashed via `_hashEmporiumOps`), so the attacker cannot alter what calls execute — including any `invokeWallet` call that legitimately moves ERC20 tokens out of the signer's `HinkalWallet` (`callHinkalWallet`, gated `onlyEmporium`): [3](#0-2) 

After `ops` run, `runAction` measures the Emporium contract's own balance delta for whatever `circomData.erc20TokenAddresses` the *caller* (prover) chose, and hands the delta to `handleOut`, which transfers it to `msg.sender` (i.e., `Hinkal.sol`) and mints a new UTXO addressed to `circomData.stealthAddressStructure` — fully attacker-controlled: [4](#0-3) 

Back in `Hinkal.sol`, the outer bookkeeping only requires `balanceDif == amountChanges[i] + utxoAmount`, which is a purely self-consistent constraint the attacker's own ZK proof can satisfy trivially by declaring `amountChanges[i] = 0` (no change to their pre-existing shielded balance) and letting the entire real balance increase be captured as a freshly-created `utxoAmount` UTXO under their own commitment: [5](#0-4) 

Nothing in `performHinkalChecks`, `dimensionsCheck`, or `checkOnchainCreation` ties `erc20TokenAddresses`/`amountChanges`/`stealthAddressStructure` to the Emporium owner's identity — those checks only validate array-length consistency and relay whitelisting, not authorization of value destination: [6](#0-5) 

**Exploit flow:** Attacker observes/obtains a valid, unused `EmporiumStack` (signed by a victim) whose `ops` legitimately withdraw ERC20 tokens from the victim's `HinkalWallet` into the Emporium contract (e.g. `invokeWallet=true` op). Before the victim's own relayer/proof submits it, the attacker crafts their own proof for `Hinkal.transact` using the same `stack` (same `emporiumMessage`, not yet marked used) but with `circomData.erc20TokenAddresses` = [stolen token], `amountChanges[i] = 0`, `inputNullifiers[i]` all zero (no real funds needed), `outCommitments`/`stealthAddressStructure` pointing to the attacker's own shielded address. `verifyWallet` passes (signature only covers `ops`/`maxFee`/`deadline`/`message`), `usedMessages[emporiumMessage]` is set, `ops` execute (moving the victim's tokens from wallet into Emporium), and the resulting balance increase is minted as a new UTXO credited to the attacker instead of the victim.

One caveat found during verification: redirecting the Emporium relay-fee (`payRelayFees`/`sendToRelayFromWallet`) to an attacker-controlled address is blocked, because `circomData.relay` must be `address(0)` or pass `relayerIsValid` (`tx.origin == relay && isRelayInList(relay)`), and the attacker is explicitly not a whitelisted relay. So the exploitable path is specifically the UTXO-credit redirection via `erc20TokenAddresses`/`amountChanges`/`stealthAddressStructure`, not the relay-fee path.

### Impact Explanation
Direct theft of shielded/in-flight funds: real ERC20 tokens that the wallet owner authorized moving out of their `HinkalWallet` via signed `ops` end up minted as a shielded UTXO owned by the attacker rather than the signer, with no requirement that the attacker hold or spend any of their own prior value. This is a proof/authorization-binding bypass matching the Critical category (theft of wallet funds, minting shielded value without backing). It is repeatable for every valid, unconsumed `EmporiumStack` the attacker can observe before it is executed.

### Likelihood Explanation
Preconditions: a signed, unexpired, not-yet-`usedMessages` `EmporiumStack` whose `ops` include at least one `invokeWallet` call that transfers real ERC20 value out of `stack.signerAddress` (a `HinkalWallet`) into the Emporium contract, and the attacker must see/obtain this stack before it is legitimately submitted (e.g., via mempool observation, a shared/leaked signature, or a relay flow that exposes the signed payload prior to execution). Attacker cost is only gas plus proof generation (no capital, since `amountChanges` can be zero); feasibility is high for anyone monitoring pending Emporium transactions, and the race is a simple front-run.

### Recommendation
Bind the fields that determine the value destination/amount into the EIP-712 signature (or otherwise cryptographically tie them to the signer), e.g. include a hash of `circomData.erc20TokenAddresses`, `deltaAmountChanges`/`amountChanges`, and `circomData.stealthAddressStructure` (or an explicit "beneficiary" field chosen by the signer) inside `EMPORIUM_SIGNATURE_TYPEHASH`, so `verifyWallet` rejects any execution whose declared token/amount/recipient set differs from what the signer approved.

### Proof of Concept
Hardhat fork test:
1. Deploy `Hinkal`, `EmporiumUpgradeable`, `HinkalWallet` per repo test scaffolding; fund `HinkalWallet` with an ERC20 token.
2. Have the "victim" sign an `EmporiumStack` whose single op is `invokeWallet=true`, `endpoint=erc20.address`, `callData=transfer(emporiumAddress, X)` — a legitimate self-withdrawal intended for the victim's own shielded balance.
3. As the attacker (no capital, no relation to the victim), generate a proof for `Hinkal.transact` reusing the same `stack`/`emporiumMessage`, but with `circomData.erc20TokenAddresses=[erc20.address]`, `amountChanges=[0]`, `inputNullifiers=[[0,0]]`, `outCommitments` computed for amount `X` under the attacker's own `stealthAddressStructure`.
4. Assert `verifyWallet` does not revert (signature check passes), `runAction` executes the `transfer` from the wallet, and the resulting UTXO (spendable by the attacker's keys) equals `X` while the victim's intended UTXO commitment is never created — demonstrating `balanceDif == amountChanges[i] (0) + utxoAmount (X)` is satisfied entirely under attacker control, proving the equality (signed authorization == actual beneficiary) is broken.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-184)
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

            UTXO memory utxoOut = handleOut(balanceChange, circomData, i);

            if (utxoOut.amount > 0) {
                utxoSet[utxoSetLength++] = utxoOut;
            }
        }

        if (utxoSetLength < circomData.erc20TokenAddresses.length) {
            utxoSet.skipLast(
                circomData.erc20TokenAddresses.length - utxoSetLength
            );
        }

        return utxoSet;
    }

    function handleOut(
        int256 balanceChange,
        CircomData calldata circomData,
        uint256 i
    ) internal returns (UTXO memory outUtxo) {
        // total change can be less than zero if there was some balance before the call -> that's why we have <=
        if (balanceChange <= 0) {
            return outUtxo;
        }

        transferERC20TokenOrETH(
            circomData.erc20TokenAddresses[i],
            msg.sender,
            uint256(balanceChange)
        );

        outUtxo = UTXO(
            uint256(balanceChange),
            circomData.erc20TokenAddresses[i],
            circomData.stealthAddressStructure,
            circomData.timeStamp
        );
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-349)
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

        if (block.timestamp > stack.deadline) {
            revert SignatureExpired();
        }

        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
    }
```

**File:** contracts/external-actions/emporium/HinkalWallet.sol (L28-34)
```text
    function callHinkalWallet(
        address endpoint,
        bytes calldata data,
        uint value
    ) external onlyEmporium returns (bool success, bytes memory err) {
        (success, err) = endpoint.call{value: value}(data);
    }
```

**File:** contracts/Hinkal.sol (L97-147)
```text
            for (uint64 i; i < circomData.erc20TokenAddresses.length; i++) {
                int256 balanceDif;

                if (circomData.erc20TokenAddresses[i] == address(0)) {
                    balanceDif =
                        int256(newBalances[i]) +
                        int256(msg.value) -
                        int256(oldBalances[i]);
                } else {
                    balanceDif =
                        int256(newBalances[i]) -
                        int256(oldBalances[i]);
                }
                // balance inequality to check that minimum amount of token is received/given
                require(
                    balanceDif >= circomData.slippageValues[i],
                    "slippage param is violated"
                );

                uint256 utxoAmount = 0;
                for (uint j = 0; j < utxoSet.length; j++) {
                    if (
                        utxoSet[j].erc20Address ==
                        circomData.erc20TokenAddresses[i]
                    ) {
                        utxoAmount += utxoSet[j].amount;

                        onChainCommitments[
                            onChainCommitmentCounter
                        ] = createOnchainCommitment(
                            utxoSet[j],
                            circomData.onChainEncryptedOutput
                        );
                        onChainCommitmentCounter++;
                    }
                }

                // balance equation to check: CHANGE IN BALANCE SHOULD EQUAL TO
                // 1) change in off-chain utxos
                // 2) change in on-chain utxos
                require(
                    balanceDif ==
                        (
                            circomData.onChainCreation[i]
                                ? int256(0)
                                : circomData.amountChanges[i]
                        ) +
                            int256(utxoAmount),
                    "Balance Diff Should be equal to sum of onchain and offchain created commitments"
                );
            }
```

**File:** contracts/HinkalHelper.sol (L64-171)
```text
    function dimensionsCheck(
        CircomData calldata circomData,
        Dimensions calldata dimensions
    ) internal pure {
        require(
            circomData.erc20TokenAddresses.length == dimensions.tokenNumber,
            "erc20TokenAddresses number should be equal to token number"
        );
        require(
            circomData.amountChanges.length == dimensions.tokenNumber,
            "AmountChanges number should be equal to token number"
        );

        require(
            circomData.onChainCreation.length == dimensions.tokenNumber,
            "onchain creation is equal to tokens count"
        );

        require(
            circomData.slippageValues.length == dimensions.tokenNumber,
            "slippageValues length should be equal to tokens count"
        );

        require(
            circomData.inputNullifiers.length == dimensions.tokenNumber,
            "InputNullifiers number should be equal to token number"
        );

        uint previousNullifierAmount = circomData.inputNullifiers.length > 0
            ? circomData.inputNullifiers[0].length
            : 0;
        for (uint i = 1; i < circomData.inputNullifiers.length; i++) {
            require(
                circomData.inputNullifiers[i].length == previousNullifierAmount,
                "Nullifier amount should be equal"
            );
        }
        require(
            previousNullifierAmount == dimensions.nullifierAmount,
            "Actual and Claimed Nullifier Amount should be equal"
        );

        require(
            circomData.outCommitments.length == dimensions.tokenNumber,
            "OutCommitments number should be equal to token number"
        );

        uint previousCommitmentAmount = circomData.outCommitments.length > 0
            ? circomData.outCommitments[0].length
            : 0;

        for (uint i = 1; i < circomData.outCommitments.length; i++) {
            require(
                circomData.outCommitments[i].length == previousCommitmentAmount,
                "Commitment amount should be equal"
            );
        }
        require(
            previousCommitmentAmount == dimensions.outputAmount,
            "Actual and Claimed Commitment Amount should be equal"
        );

        require(
            circomData.encryptedOutputs.length == dimensions.tokenNumber,
            "EncryptedOutputs number should be equal to token number"
        );

        uint previousEncryptedOutputAmount = circomData
            .encryptedOutputs
            .length > 0
            ? circomData.encryptedOutputs[0].length
            : 0;

        for (uint i = 0; i < circomData.encryptedOutputs.length; i++) {
            require(
                circomData.encryptedOutputs[i].length ==
                    previousEncryptedOutputAmount,
                "Encrypted output amount should be equal"
            );

            for (uint j = 0; j < circomData.encryptedOutputs[i].length; j++) {
                require(
                    circomData.encryptedOutputs[i][j].length > 0,
                    "Missing encrypted output for off-chain commitment"
                );
            }
        }

        require(
            previousEncryptedOutputAmount == dimensions.outputAmount,
            "Actual and Claimed Encrypted Output Amount should be equal"
        );

        require(
            circomData.onChainEncryptedOutput.length > 0,
            "Missing encrypted output for on-chain commitment"
        );

        require(
            circomData.stealthAddressStructure.H0x != 0,
            "H0x cannot be zero"
        );

        require(
            circomData.feeStructure.variableRate <= 10000,
            "Variable rate cannot be greater than 10000"
        );
    }
```
