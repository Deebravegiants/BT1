### Title
On-chain UTXOs created via `DepositOnChainUtxosExternalAction` use a caller-controlled `timeStamp` instead of `block.timestamp`, enabling commitment collisions that permanently freeze a real value-bearing leaf - (`contracts/external-actions/DepositOnChainUtxosExternalAction.sol`)

### Summary
`DepositOnChainUtxosExternalAction` builds the commitment for every new on-chain UTXO using `circomData.timeStamp + utxoIndex`, a value fully chosen by the calling EOA, instead of `block.timestamp` used everywhere else in the codebase. Because the on-chain commitment is `Poseidon(amount, erc20Address, stealthAddress, timeStamp)` and the nullifier is a deterministic function of that commitment plus the owner's private key (independent of the leaf's tree index), any depositor can reproduce the exact `(amount, erc20Address, stealthAddress, timeStamp)` tuple of an existing on-chain UTXO — whose fields are emitted in cleartext via `NewCommitment` — and insert a second, cryptographically identical leaf. Once the true owner spends either leaf, the shared nullifier is marked used, and the other identical leaf (backed by real, transferred tokens) becomes permanently unspendable.

### Finding Description
`DepositOnChainUtxosExternalAction.runAction` constructs each output UTXO as: [1](#0-0) 

with the explicit design note that these commitments are "fully determined by the caller, because their timestamps come from `circomData.timeStamp` rather than from the block": [2](#0-1) 

`createOnchainCommitment` in `HinkalBase.sol` then hashes exactly those four fields into the leaf commitment: [3](#0-2) 

This is inconsistent with every other UTXO-creation path in the protocol, which binds the commitment to `block.timestamp`: [4](#0-3) [5](#0-4) 

The nullifier that later prevents double-spending is derived purely from the commitment and the spender's private key material, with no dependency on the leaf's tree index: [6](#0-5) 

and the on-chain nullifier registry is a flat, global mapping keyed only by nullifier value: [7](#0-6) 

Finally, on-chain UTXO details (`amount`, `erc20Address`, `stealthAddressStructure`, `timeStamp`) are emitted in cleartext for every on-chain commitment, so an attacker can read the exact fields of any existing on-chain UTXO from chain history: [8](#0-7) 

Because `timeStamp` (and thus the whole commitment pre-image) is entirely attacker-chosen in `DepositOnChainUtxosExternalAction`, an attacker can observe a target's on-chain UTXO fields from a `NewCommitment` event and call `Hinkal.transact` → `DepositOnChainUtxosExternalAction` again with the same `amount`, `erc20Address`, `stealthAddressStructure`, and a `timeStamp` chosen so that `circomData.timeStamp + utxoIndex` equals the target's original `timeStamp`. This produces a second leaf with an identical Poseidon commitment. `Hinkal.transact`'s balance-equation check only verifies that the attacker actually paid in the token amount for their own new UTXOs — it does not check leaf uniqueness — so the duplicate leaf is legitimately inserted into the Merkle tree: [9](#0-8) 

Since both leaves hash to the same commitment, the true owner's spend of either one produces the identical nullifier. The nullifier is recorded once in the global `nullifiers` mapping, and any subsequent attempt to spend the other, still value-bearing leaf reverts with `"Nullifier cannot be reused"`, permanently trapping the tokens that back that leaf.

### Impact Explanation
This breaks the "every leaf the tree accepts corresponds to a uniquely spendable value" invariant: two economically distinct deposits collapse into a single spendable unit, permanently freezing the real ERC20/ETH value backing the leaf that is never spent. If the colliding stealth address belongs to a third-party recipient who was legitimately receiving two separate deposits of the same amount/token (a realistic scenario for round, commonly-used deposit amounts sent to a repeatedly-used/public stealth address), the recipient can only ever redeem one of the two deposits — the other's value is irrecoverably locked in the Hinkal contract. This matches the "permanent freezing of user funds" and "value-bearing leaf left unspendable" impact categories.

### Likelihood Explanation
The attacker needs no privileged role — any EOA can call `Hinkal.transact` targeting `DepositOnChainUtxosExternalAction`. The only precondition is reading a target's existing on-chain UTXO fields, which are broadcast in cleartext by `NewCommitment`, and supplying matching `amount`/`erc20Address`/`stealthAddressStructure`/`timeStamp` — all of which are attacker-controlled inputs to this specific external action. No cryptographic secrets of the victim are required to create the colliding leaf (only to eventually redeem it), making the collision trivial to engineer once a target UTXO is observed on-chain.

### Recommendation
Bind the on-chain UTXO's `timeStamp` field to `block.timestamp` in `DepositOnChainUtxosExternalAction.sol`, exactly as done in `Hinkal.sol::_createProoflessDepositCommitments` and `ExternalActionSwap.sol::swap`, removing the caller's ability to fully control the commitment pre-image. If distinct timestamps per UTXO within a batch are still needed, derive the increment from `block.timestamp` plus a bounded, monotonic index rather than an arbitrary caller-supplied base value.

### Proof of Concept
1. Victim (or attacker on victim's behalf) calls `Hinkal.transact` with `externalActionData.externalActionId` set to `DepositOnChainUtxosExternalAction`, depositing `amount = 100e18` of token `T` to `stealthAddressStructure = S` with `circomData.timeStamp = 1000`, `utxoIndex = 0` → on-chain leaf `L1` with `commitment = Poseidon(100e18, T, S.stealthAddress, 1000)` is inserted; `NewCommitment` emits the full `UTXO{amount:100e18, erc20Address:T, stealthAddressStructure:S, timeStamp:1000}` in cleartext.
2. Attacker reads this event, then calls `Hinkal.transact` again through the same external action with `originalSender = attacker`, `amount = 100e18` of `T`, the **same** `stealthAddressStructure = S`, and `circomData.timeStamp = 1000`, `utxoIndex = 0` → attacker pays `100e18` of `T` from their own wallet, and leaf `L2` is inserted with an identical `commitment`.
3. The true owner of `S` later spends `L1` normally, producing nullifier `N = f(commitment, signature)` and setting `nullifiers[N] = true` in `HinkalBase.sol`.
4. The true owner (or anyone with the private key for `S`) attempts to spend `L2` using a valid Merkle-inclusion proof for `L2` — the circuit computes the same nullifier `N`, and `insertNullifiers` reverts with `"Nullifier cannot be reused"`, permanently freezing the `100e18` of `T` behind `L2`.

### Citations

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L10-13)
```text
/// @title DepositOnChainUtxosExternalAction
/// @notice Deposits tokens into Hinkal and creates on-chain UTXOs whose commitments
/// are fully determined by the caller, because their timestamps come from
/// circomData.timeStamp rather than from the block.
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L66-72)
```text
                utxoSet[utxoIndex] = UTXO({
                    amount: amount,
                    erc20Address: tokenAddress,
                    stealthAddressStructure: circomData.stealthAddressStructure,
                    timeStamp: circomData.timeStamp + utxoIndex
                });
                utxoIndex++;
```

**File:** contracts/HinkalBase.sol (L53-62)
```text
    function createOnchainCommitment(
        UTXO memory utxo,
        bytes calldata onChainEncryptedOutput
    ) internal view returns (OnChainCommitment memory) {
        uint256 commitment = hash4(
            utxo.amount,
            uint256(uint160(utxo.erc20Address)),
            utxo.stealthAddressStructure.stealthAddress,
            utxo.timeStamp
        );
```

**File:** contracts/HinkalBase.sol (L122-131)
```text
            for (uint256 i = 0; i < onChainCommitments.length; i++) {
                emit NewCommitment(
                    leaves[index],
                    -1 * int256(insertedIndexes[index++]),
                    abi.encode(
                        onChainCommitments[i].utxo,
                        onChainCommitments[i].onChainEncryptedOutput
                    )
                );
            }
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

**File:** contracts/Hinkal.sol (L116-146)
```text
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
```

**File:** contracts/Hinkal.sol (L336-346)
```text
        for (uint256 i = 0; i < length; i++) {
            onChainCommitmentsArray[i] = createOnchainCommitment(
                UTXO({
                    amount: amounts[i],
                    erc20Address: erc20Addresses[i],
                    stealthAddressStructure: stealthAddressStructures[i],
                    timeStamp: block.timestamp
                }),
                onChainEncryptedOutputs[i]
            );
        }
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L95-101)
```text
        utxoSet = new UTXO[](1);
        utxoSet[0] = UTXO({
            amount: amountToSendToHinkal,
            erc20Address: outputToken,
            stealthAddressStructure: circomData.stealthAddressStructure,
            timeStamp: block.timestamp
        });
```

**File:** circuits/MainEVMCircuit.circom (L114-134)
```text
        // 1) Calculating Commitments for Input UTXOs
        calcCommitment[i][j] = OriginalCommitmentCalculator();
        calcCommitment[i][j].amount <== inAmounts[i][j];
        calcCommitment[i][j].erc20TokenAddress <== erc20TokenAddresses[i];
        calcCommitment[i][j].publicKey <== calcInPublicKeys[i][j].out;
        calcCommitment[i][j].timeStamp <== inTimeStamps[i][j];

        preventInOverflow[i][j] = OverflowPreventer(inputCount);
        preventInOverflow[i][j].in <== inAmounts[i][j];

        // 2) Calculating Nullifier from commitment and signature
        calcSignature[i][j] = Signature();
        calcSignature[i][j].nullifyingPrivateKey <== nullifyingPrivateKey;
        calcSignature[i][j].commitment <== calcCommitment[i][j].out;

        calcNullifier[i][j] = NullifierCalculator();
        calcNullifier[i][j].commitment <== calcCommitment[i][j].out;
        calcNullifier[i][j].signature <== calcSignature[i][j].out;

        // 3) Checking that nullifier is legit
        inNullifiers[i][j] === calcNullifier[i][j].out;
```
