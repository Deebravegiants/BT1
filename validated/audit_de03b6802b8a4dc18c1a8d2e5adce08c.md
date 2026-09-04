### Title
EmporiumStack signature omits destination and fee fields, letting anyone reroute a signed wallet action's proceeds to their own stealth address - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`verifyWallet` recovers the EIP-712 signature over `EMPORIUM_SIGNATURE_TYPEHASH`, which binds only `(emporiumMessage, opsHash, maxFee, deadline)`. It does not bind `circomData.stealthAddressStructure`, `circomData.erc20TokenAddresses`, `circomData.feeStructure`, `circomData.relay`, `deltaAmountChanges`, or `circomData.onChainCreation`. Since any unprivileged caller of `Hinkal.transact` fully controls `CircomData` for their own submitted proof, they can wrap a previously-signed `EmporiumStack` (obtained from the mempool, a relay UI, or any prior broadcast) inside new `CircomData` that redirects the proceeds of the signer's authorized wallet operations to the attacker's own shielded stealth address, especially cheaply when `onChainCreation[i]` is true for the affected token.

### Finding Description
The invariant that should hold is: `(assets leaving stack.signerAddress's wallet, their destination) == (ops, maxFee) authorized by the owner's signature`. In practice the destination of any surplus produced by the ops is set by `circomData.stealthAddressStructure`, which is never part of the signed payload.

Trace:
- `verifyWallet` (contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:302-349) hashes only `EMPORIUM_SIGNATURE_TYPEHASH` = `(message, opsHash, maxFee, deadline)` via `_hashTypedDataV4`. [1](#0-0) 
- `runAction` executes `stack.ops` against `stack.signerAddress`'s `HinkalWallet` (fixed, hash-bound calls), then computes `balanceChange` for each `circomData.erc20TokenAddresses[i]` and calls `handleOut`. [2](#0-1) 
- `handleOut` builds the resulting `UTXO` using `circomData.stealthAddressStructure` — an attacker-controlled, unsigned field — as the note's owner/destination. [3](#0-2) 
- The wallet-signature integrity check `calldataHash == getHashedCalldata(circomData)` only proves the submitted `CircomData` is self-consistent; it does not prove any of `stealthAddressStructure`, `feeStructure`, `relay`, or `erc20TokenAddresses` were approved by `stack.signerAddress`. [4](#0-3) [5](#0-4) 
- `checkOnchainCreation` only requires the action be external and `amountChanges[i]==0`/`inputNullifiers[i]==0`, with no constraint tying the resulting on-chain UTXO's `stealthAddressStructure` to the signer. [6](#0-5) 
- The Hinkal balance equation, when `onChainCreation[i]` is true, drops the `amountChanges[i]` term entirely (`balanceDif == utxoAmount`), so the whole positive surplus produced by the signer's ops is captured purely as a new on-chain UTXO carrying the attacker-chosen `stealthAddressStructure`, with zero ZK-circuit constraint over its ownership for that index (off-chain nullifier/commitment loops `break` when `onChainCreation[i]==true`). [7](#0-6) [8](#0-7) 

Exploit flow: attacker obtains a valid `(v,r,s)` over `(emporiumMessage, ops, maxFee, deadline)` signed by a wallet owner for some legitimate purpose (e.g. captured from a broadcast/mempool tx before it lands, or leaked by a relay's frontend prior to submission). Attacker then calls `Hinkal.transact` themselves with a locally generated valid proof for their own (possibly trivial) UTXO state, setting `circomData.externalActionData.externalActionMetadata` to the captured `EmporiumStack`, `circomData.stealthAddressStructure` to their own stealth key, `circomData.erc20TokenAddresses`/`onChainCreation[i]=true` for the token the ops will surface, and `circomData.relay`/`feeStructure` to whatever they like (subject only to `flatFee <= stack.maxFee`). `verifyWallet` succeeds because the signature only checks `(message, opsHash, maxFee, deadline)`, all reused verbatim. The ops run against the real signer's wallet, any resulting balance surplus is swept and shielded to the attacker's stealth address instead of the signer's.

### Impact Explanation
The wallet owner's assets, moved by ops they did authorize, end up shielded under a destination (stealth address) they never authorized — an unprivileged third party executes a call/asset movement whose *destination* the signer never signed. This matches the "High: executing calls or moving assets a wallet owner or prover never authorised" category. It is repeatable for every signed `EmporiumStack` an attacker can observe/capture whose `deadline` remains in the future and whose `emporiumMessage` has not yet been consumed by the legitimate flow (a race the attacker can win by front-running, since `usedMessages` is a simple boolean set on first successful call regardless of caller).

### Likelihood Explanation
Preconditions: attacker needs to obtain a valid, unused, un-expired `EmporiumStack` signature (visible in mempool before its intended tx lands, or leaked via a relay/dApp before submission) and be able to submit their own valid `Hinkal.transact` call with a locally-generated proof for their own funds/UTXO state (fully within the described "unprivileged attacker" capability set — deposit own funds, generate own proofs, craft any `CircomData` field). Cost is one transaction plus proof generation; the race against the legitimate submission is the only real constraint, made easier by the front-runnable, per-message (not per-caller) replay guard.

### Recommendation
Expand `EMPORIUM_SIGNATURE_TYPEHASH` to bind every field of `CircomData` that determines where funds end up and how fees are computed: `stealthAddressStructure`, `erc20TokenAddresses`, `feeStructure` (all fields, not just `flatFee <= maxFee`), `relay`, and `onChainCreation`/`deltaAmountChanges` semantics for the tokens touched by the ops. Alternatively, require `stack.signerAddress` (or a designated beneficiary address explicitly included in the signed struct) to be the sole valid destination/`stealthAddress` for any UTXO produced from `handleOut`, and validate that on-chain within `runAction`/`handleOut`.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, a `HinkalWallet` for `signer`, and a test endpoint whose call unstakes/transfers tokens from the wallet into the Emporium contract (a legitimate, wallet-owner-approved op).
2. Have `signer` sign an `EmporiumStack` (`ops`, `maxFee`, far-future `deadline`, fresh `emporiumMessage`) intending proceeds to return to their own shielded balance (their own `stealthAddressStructure`).
3. As `attacker` (a different EOA, never given the signature by the protocol, simply having observed it), submit `Hinkal.transact` with locally-generated proof for `attacker`'s own trivial UTXO, `circomData.externalActionData.externalActionMetadata = abi.encode(signedStack)`, `circomData.stealthAddressStructure = attackerStealth`, `circomData.onChainCreation[i] = true` for the surplus token, `deltaAmountChanges[i] = 0`.
4. Assert: (a) call succeeds (`verifyWallet` passes); (b) the resulting `NewCommitment`/UTXO emitted encodes `attackerStealth`, not `signerStealth`; (c) `stack.signerAddress`'s wallet balance decreased by the ops' effect while no shielded note under `signerStealth` was created — i.e. `(destination signed by owner) != (destination actually credited)`.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-151)
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L162-184)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L318-340)
```text
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

**File:** contracts/HinkalHelper.sol (L173-202)
```text
    function checkOnchainCreation(
        CircomData calldata circomData
    ) internal pure {
        bool isInternalTransaction = circomData
            .externalActionData
            .externalActionId == 0;

        for (uint i = 0; i < circomData.onChainCreation.length; i++) {
            if (circomData.onChainCreation[i]) {
                require(
                    !isInternalTransaction,
                    "onChainCreation not allowed for internal transactions"
                );
                require(
                    circomData.amountChanges[i] == 0,
                    "amountChanges must be zero when onChainCreation is true"
                );
                for (
                    uint j = 0;
                    j < circomData.inputNullifiers[i].length;
                    j++
                ) {
                    require(
                        circomData.inputNullifiers[i][j] == 0,
                        "inputNullifiers must be zero when onChainCreation is true"
                    );
                }
            }
        }
    }
```

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
```

**File:** contracts/CircomDataBuilder.sol (L10-54)
```text
    function getHashedCalldata(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        // because of stack too deep error, we need to split the calldata into two parts
        uint256 calldataHash1 = getHashedCalldata1(circomData);
        uint256 calldataHash2 = getHashedCalldata2(circomData);
        return (uint256(keccak256(abi.encode(calldataHash1, calldataHash2))) %
            CIRCOM_P);
    }

    function getHashedCalldata1(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.publicSignalCount,
                        circomData.relay,
                        circomData.emporiumMessage,
                        circomData.externalActionData,
                        circomData.slippageValues
                    )
                )
            );
    }

    function getHashedCalldata2(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.hookData,
                        circomData.encryptedOutputs,
                        circomData.onChainEncryptedOutput,
                        circomData.feeStructure,
                        circomData.onChainCreation,
                        circomData.originalSender,
                        circomData.extraData
                    )
                )
            );
    }
```

**File:** contracts/Hinkal.sol (L134-146)
```text
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
```

**File:** contracts/HinkalBase.sol (L135-152)
```text
    function insertNullifiers(
        uint256[][] calldata inputNullifiers,
        bool[] calldata onChainCreation
    ) internal {
        for (uint256 i = 0; i < inputNullifiers.length; i++) {
            for (uint256 j = 0; j < inputNullifiers[i].length; j++) {
                if (onChainCreation[i] == true) break;
                if (inputNullifiers[i][j] != 0) {
                    require(
                        !nullifiers[inputNullifiers[i][j]],
                        "Nullifier cannot be reused"
                    );
                    nullifiers[inputNullifiers[i][j]] = true;
                    emit Nullified(inputNullifiers[i][j]);
                }
            }
        }
    }
```
