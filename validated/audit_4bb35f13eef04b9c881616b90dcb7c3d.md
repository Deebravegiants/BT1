### Title
Balance-mirroring token entry lets attacker mint unbacked shielded UTXOs via double-counted `erc20TokenAddresses` in `Hinkal.transact` - (File: contracts/Hinkal.sol)

### Summary
`Hinkal.transact` verifies token-flow correctness per index of `circomData.erc20TokenAddresses` by snapshotting `balanceOf` before/after and requiring `balanceDif == amountChanges[i] + utxoAmount` for each index independently [1](#0-0) . Neither the on-chain code nor the circuit's `distinctErc20AddressChecks` verify that two different token addresses actually correspond to independent balances - the circuit only checks the numeric field-element values differ [2](#0-1) . An attacker who deploys a "mirror" token whose `balanceOf(Hinkal)` reads another real token's stored balance can insert that mirror address as an extra `erc20TokenAddresses` entry and get a second, fully unbacked shielded UTXO credited for the same single real balance change.

### Finding Description
The broken equality is: **real value received by Hinkal == total value credited as shielded UTXOs/off-chain amountChanges**. The code enforces this per-index via `balanceDif == (onChainCreation[i] ? 0 : amountChanges[i]) + utxoAmount` where `oldBalances`/`newBalances` come from `getBalancesForArray` calling `balanceOf` on each `erc20TokenAddresses[i]` [3](#0-2) .

Attack construction:
1. Attacker deploys `TokenA` (optionally fee-on-transfer) and `TokenB`, a contract whose `balanceOf(addr)` simply forwards to/returns `TokenA.balanceOf(addr)` — i.e., `TokenB` mirrors `TokenA`'s real balance for the Hinkal contract without holding any independent value.
2. Attacker calls `Hinkal.transact` with `dimensions.tokenNumber = 3` (e.g. via a LiFi swap `externalActionId`), setting `erc20TokenAddresses = [inputToken, TokenA, TokenB]`. The circuit's `distinctErc20AddressChecks` passes because `TokenA != TokenB` as raw addresses [2](#0-1) .
3. `_externalTransact` routes to `ExternalActionSwap.swap`, which swaps `erc20TokenAddresses[0]` for `erc20TokenAddresses[1]` (`TokenA`) using balance-delta accounting that correctly handles fee-on-transfer, then sends the real delivered amount `Z` back to Hinkal and returns a UTXO with `erc20Address = TokenA, amount = Z` [4](#0-3) .
4. Because `TokenB.balanceOf(Hinkal)` mirrors `TokenA.balanceOf(Hinkal)`, the same real transfer of `Z` also shows up as `balanceDif[2] = Z` for the `TokenB` index, even though no real value moved for `TokenB`.
5. The attacker sets `amountChanges[2] = Z` (with `onChainCreation[2] = false`) for the `TokenB` slot. Crucially, `_externalTransact` only performs a real transfer when `deltaAmountChanges[i] < 0`; it never enforces any inbound transfer for a **positive** `amountChanges[i]` [5](#0-4) . So the `TokenB` "deposit" requires no real transfer call at all.
6. The post-loop check for index 2 then verifies `balanceDif[2] (Z) == amountChanges[2] (Z) + utxoAmount(0)`, which holds, letting the transaction proceed and mint a brand-new off-chain output commitment for `TokenB` worth `Z`, satisfied purely by the circuit's `inTotal + amountChanges[i] === outTotal` equation with `inTotal = 0` [6](#0-5) .

Net result: a single real balance delta of `Z` (from the swap) is credited twice — once as the legitimate `TokenA` UTXO and once as a wholly unbacked `TokenB` shielded note — doubling the shielded value minted relative to the value actually received by the vault. This works identically (and even more simply) through `_internalTransact`, where the fake `TokenB` "deposit" transfer is a no-op call to an attacker-controlled `transferFrom` that always returns success without moving real assets, while `balanceOf` still mirrors `TokenA`.

None of the existing guards catch this: `performHinkalChecks`/`dimensionsCheck` only validate array-length consistency, not balance independence [7](#0-6) ; `checkOnchainCreation` only restricts on-chain creation semantics [8](#0-7) ; the circuit's distinctness check is purely a numeric address comparison [2](#0-1) .

### Impact Explanation
The attacker mints a fully unbacked shielded UTXO (in this scenario worth `Z`, equal to whatever real value the swap already delivered) that can later be spent/withdrawn like any legitimate shielded balance, directly draining the vault of assets it never received — protocol insolvency. This satisfies the Critical category: "minting shielded value without backing." The attack is repeatable per transaction and scales with the swap size, limited only by gas costs of deploying the mirror token and the size of the swap performed to seed the initial real balance delta.

### Likelihood Explanation
Preconditions are fully within an unprivileged attacker's control: deploying an arbitrary mirror ERC20 contract, choosing `tokenNumber`/`dimensions` for an existing registered verifier that supports 3+ tokens, and crafting `CircomData` fields including `erc20TokenAddresses`, `amountChanges`, `onChainCreation`, and generating a valid proof for their own UTXOs — all explicitly permitted by the rules. The only dependency is that a verifier is registered for the chosen `(tokenNumber, nullifierAmount, outputAmount, externalActionId)` combination via `buildVerifierId`/`verifierMap` [9](#0-8) ; if such a verifier exists (e.g., a generic multi-token swap/emporium circuit supporting 3 tokens), the exploit is straightforward and cheap, requiring no interaction with any victim or privileged role.

### Recommendation
- Do not rely solely on `balanceOf` snapshots per declared address for solvency accounting. Require that each `erc20TokenAddresses[i]` used in a swap/external action be an allow-listed, vetted token contract, or independently verify that token contracts are not proxies/mirrors of one another before trusting their `balanceOf`.
- In `_externalTransact`, also require and perform a real inbound transfer (or equivalent enforced value movement) for entries with positive `amountChanges[i]`, mirroring the behavior in `_internalTransact`, rather than silently trusting the balance-diff check alone.
- Track a single canonical running "total value received into Hinkal this transaction" instead of independently trusting `balanceOf` deltas per array index, or reconcile that the sum of independently observed balance deltas cannot exceed what any single underlying transfer justifies (e.g., disallow reusing/aliasing balance state across distinct addresses within one call by, for example, requiring `extcodehash`/bytecode uniqueness checks or an owner-curated token allowlist for `erc20TokenAddresses`).

### Proof of Concept
Foundry test plan:
1. Deploy `TokenA` (standard ERC20, optionally fee-on-transfer) and `TokenB` (malicious "mirror" contract whose `balanceOf(a)` returns `TokenA.balanceOf(a)`, and whose `transferFrom`/`transfer` are no-ops that always return `true`).
2. Register a verifier for `dimensions.tokenNumber = 3` with the target `externalActionId` (LiFi swap) in `verifierMap`, and produce a real local proof for a transaction with `erc20TokenAddresses = [inputToken, TokenA, TokenB]`.
3. Fund attacker with `inputAmount` of `inputToken`; craft `externalActionMetadata` so the LiFi router swaps `inputToken` → `TokenA` yielding `Z` tokens actually delivered to Hinkal.
4. Set `amountChanges = [-inputAmount(adjusted), 0, Z]`, `onChainCreation = [false, false, false]`, with a fresh off-chain output commitment of value `Z` for the `TokenB` slot (no input nullifiers needed since `inTotal=0`).
5. Call `Hinkal.transact(...)`.
6. Assert: (a) `TokenA.balanceOf(hinkal)` increases by exactly `Z` (the real swap output); (b) the transaction succeeds and inserts a new shielded commitment crediting `Z` for `TokenB`; (c) total shielded value credited (`Z` for `TokenA` UTXO + `Z` for `TokenB` off-chain note = `2Z`) exceeds the real value received by Hinkal (`Z`), i.e. `vault_balance_delta (Z) < credited_UTXO_value (2Z)` — confirming insolvency.

### Citations

**File:** contracts/Hinkal.sol (L78-146)
```text
            uint256[] memory oldBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            if (circomData.externalActionData.externalActionId == 0) {
                _internalTransact(circomData);
            } else {
                utxoSet = _externalTransact(circomData);
            }

            uint256[] memory newBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            OnChainCommitment[]
                memory onChainCommitments = new OnChainCommitment[](
                    utxoSet.length
                );
            uint256 onChainCommitmentCounter = 0;
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
```

**File:** contracts/Hinkal.sol (L244-256)
```text
        int256[] memory deltaAmountChanges = new int256[](
            circomData.erc20TokenAddresses.length
        );
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            deltaAmountChanges[i] = _calculateDeltaAmount(circomData, i);
            if (deltaAmountChanges[i] < 0) {
                transferERC20TokenOrETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    uint256(-deltaAmountChanges[i])
                );
            }
        }
```

**File:** circuits/MainEVMCircuit.circom (L152-168)
```text
    for(var j=0; j< outputCount; j++) {
      calcOutCommitment[i][j] = OriginalCommitmentCalculator();
      calcOutCommitment[i][j].amount <== outAmounts[i][j]; // if outAmount is negative, than this line will throw error
      calcOutCommitment[i][j].erc20TokenAddress <== erc20TokenAddresses[i];
      calcOutCommitment[i][j].publicKey <== outPublicKeys[i][j];
      calcOutCommitment[i][j].timeStamp <== outTimeStamp;

      // Checking that output commitment is legit
      calcOutCommitment[i][j].out === outCommitments[i][j];

      preventOutOverflow[i][j] = OverflowPreventer(outputCount);
      preventOutOverflow[i][j].in <== outAmounts[i][j];
      outTotal += outAmounts[i][j];
    }

      // for each token type, the sum of refund and swapped amount should be equal to the sum of input amounts
      inTotal + amountChanges[i] === outTotal;
```

**File:** circuits/MainEVMCircuit.circom (L171-182)
```text
  component distinctErc20AddressChecks[tokenCount * (tokenCount-1)/2];
  var index = 0;
  for (var i =0; i< tokenCount-1;i++){
    for (var j = i+1; j< tokenCount; j++)
    {
      distinctErc20AddressChecks[index] = IsEqual();
      distinctErc20AddressChecks[index].in[0] <== erc20TokenAddresses[i];
      distinctErc20AddressChecks[index].in[1] <== erc20TokenAddresses[j];
      distinctErc20AddressChecks[index].out === 0;
      index++;
    }
  }
```

**File:** contracts/Transferer.sol (L169-176)
```text
    function getBalancesForArray(
        address[] calldata erc20TokenAddresses
    ) internal view returns (uint256[] memory balances) {
        balances = new uint256[](erc20TokenAddresses.length);
        for (uint64 i; i < erc20TokenAddresses.length; i++) {
            balances[i] = getERC20OrETHBalance(erc20TokenAddresses[i]);
        }
    }
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L63-101)
```text
        uint256 swappedAmount = callRouter(
            inputToken,
            inputAmount,
            outputToken,
            circomData.externalActionData.externalActionMetadata
        );

        uint256 relayFee = circomData.feeStructure.flatFee;

        uint256 hinkalFee = hinkalHelper.calculateRelayFee(
            swappedAmount,
            0,
            circomData.feeStructure.variableRate
        );

        if (circomData.feeStructure.feeToken == outputToken) {
            sendToRelay(circomData.relay, relayFee + hinkalFee, outputToken);
        } else {
            sendToRelay(
                circomData.relay,
                relayFee,
                circomData.feeStructure.feeToken
            );
            sendToRelay(circomData.relay, hinkalFee, outputToken);
        }

        uint256 totalFee = hinkalFee +
            (outputToken == circomData.feeStructure.feeToken ? relayFee : 0);
        uint256 amountToSendToHinkal = swappedAmount - totalFee;

        transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal);

        utxoSet = new UTXO[](1);
        utxoSet[0] = UTXO({
            amount: amountToSendToHinkal,
            erc20Address: outputToken,
            stealthAddressStructure: circomData.stealthAddressStructure,
            timeStamp: block.timestamp
        });
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

**File:** contracts/VerifierFacade.sol (L28-43)
```text
    function buildVerifierId(
        Dimensions calldata dimensions,
        uint256 externalActionId
    ) public pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        dimensions.tokenNumber,
                        dimensions.nullifierAmount,
                        dimensions.outputAmount,
                        externalActionId
                    )
                )
            );
    }
```
