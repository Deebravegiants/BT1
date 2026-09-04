### Title
`balanceDif` equality in `Hinkal.transact` can be satisfied for a phantom token slot whose `balanceOf` mirrors a real token's balance, letting an attacker mint unbacked shielded value alongside a LiFi swap - ([File: contracts/Hinkal.sol])

### Summary
`Hinkal.transact` snapshots balances per `erc20TokenAddresses[i]` independently with `getBalancesForArray`/`balanceOf`, and validates each index in isolation against `amountChanges[i] + utxoAmount`. The only on-chain uniqueness guarantee on the token list is the circuit's `distinctErc20AddressChecks`, which only forces the raw *addresses* to differ - it cannot and does not verify that two distinct contract addresses report independent economic balances. An attacker who deploys a pair of token contracts where one address's `balanceOf(hinkal)` is defined to mirror the real balance movement of the other can add the mirror address as an extra `erc20TokenAddresses` slot in the same `transact` call that performs a LiFi swap, and claim an `amountChanges` credit for that slot that is "backed" by the same physical tokens already counted for the real swap output token.

### Finding Description
The invariant the contract is supposed to enforce, per index `i`:

`balanceDif[i] == (onChainCreation[i] ? 0 : amountChanges[i]) + utxoAmount[i]`

is meant to guarantee `net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts)` **only if** `balanceDif[i]` for each `i` reflects an *independent* real value movement.

`Hinkal.transact` computes `oldBalances`/`newBalances` via `getBalancesForArray(circomData.erc20TokenAddresses)`, which for each entry calls `IERC20(addr).balanceOf(address(this))` independently [1](#0-0) , then loops over every index computing `balanceDif` and checking it against `amountChanges[i] + utxoAmount[i]` [2](#0-1) .

For a LiFi swap, `ExternalActionSwap.swap` only ever reads/writes `erc20TokenAddresses[0]` (input) and `[1]` (output), and only mints one `UTXO` entry for the output token [3](#0-2) . Any further indices in `circomData.erc20TokenAddresses` (index 2, 3, ...) are never touched by the swap logic, yet `Hinkal.transact`'s balance-diff loop still validates them exactly as if they were ordinary internal-transact token slots.

The on-chain uniqueness guard, `distinctErc20AddressChecks` in `MainEVMCircuit.circom`, only forces `erc20TokenAddresses[i] != erc20TokenAddresses[j]` as raw field values [4](#0-3) . It cannot express or check "these two addresses report the same underlying balance." Since the attacker deploys the token contracts themselves, they can create address `B` whose `balanceOf(hinkal)` is defined to track the real balance of the swap's output token `A` (e.g., `B.balanceOf` forwards to `A.balanceOf`, or both read shared storage), while `A` is the actual token moved by the LiFi router call.

Exploit call:
1. Attacker builds `circomData` with `erc20TokenAddresses = [inputToken, outputTokenA, phantomTokenB]`, `externalActionData.externalActionId` set to the LiFi swap action, and a valid proof for a verifier registered for that `(tokenNumber=3, ...)` dimension/action combo.
2. The swap executes normally: real tokens move from Hinkal to router (input) and back to Hinkal (output `A`), producing exactly one `UTXO` for `A` [5](#0-4) .
3. Because `B.balanceOf(hinkal)` mirrors `A`'s balance change, `newBalances[2] - oldBalances[2]` in `Hinkal.transact` equals the same swap output amount `X`, even though no independent `B` value entered Hinkal.
4. For index 2, `utxoAmount` is `0` (no `UTXO` in `utxoSet` has `erc20Address == B`), so the check reduces to `balanceDif[2] == amountChanges[2]`. The attacker simply sets `amountChanges[2] = X` in the circuit inputs, which is legal circuit-side as long as `outAmounts` for token slot 2 sum to `inTotal + X` (satisfiable with zero real inputs, minting a fresh shielded output).
5. Result: the attacker walks away with a real `UTXO` for `A` worth `X` (from the swap) **plus** a freshly minted shielded off-chain balance of `X` for `B`, while only `X` worth of real value ever entered the vault.

This breaks the target invariant `net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)`: LHS = `X`, RHS = `X (utxoAmount for A) + X (amountChanges for B)` = `2X`.

None of the listed guards catch this: `performHinkalChecks`/`dimensionsCheck`/`checkOnchainCreation` only validate array-length consistency and simple onChainCreation rules, not balance independence [6](#0-5) ; `verifyProof` only checks the ZK relations, which are satisfied because `amountChanges[2]` is a free public input matched by attacker-chosen `outAmounts`; `rootHashExists`, `insertNullifiers`, and `onlyAllowedRecipient` are unrelated to this cross-token balance aliasing.

### Impact Explanation
The attacker mints shielded UTXO value (`amountChanges[2]` worth of "phantom token B") that is not backed by any independent transfer of value into the vault - it is backed only by the same real value already counted for the swap's real output token. If `B` is later redeemable (e.g., a token whose `transfer` shares the same underlying ledger/storage as `A`, or the attacker can later swap the shielded UTXO's claim into real assets via further protocol interactions), this constitutes minting shielded value without backing, i.e., protocol insolvency - a Critical-severity impact matching "minting shielded value without backing." The attack is repeatable per transaction and scales with the swap size and the number of extra phantom slots the attacker can fit into a single call (bounded by whatever `tokenNumber` dimension has a registered verifier).

### Likelihood Explanation
Preconditions: (1) an admin-registered verifier must exist for a `Dimensions` combination with `tokenNumber >= 3` paired with the LiFi swap `externalActionId` (nothing in `Hinkal.sol`/`HinkalHelper.sol`/`VerifierFacade.sol` restricts swap actions to exactly 2 tokens - `ExternalActionSwap.swap` simply ignores extra slots, and `buildVerifierId` derives the verifier purely from `(tokenNumber, nullifierAmount, outputAmount, externalActionId)`); (2) the attacker must deploy a token pair with cross-referencing `balanceOf` semantics, which is fully within the stated attacker capabilities ("deploy contracts... deploy the token"). Whether such a multi-token-plus-swap verifier is actually deployed in production cannot be confirmed from this repository alone - it depends on off-chain deployment configuration not visible in the code. If it is deployed (which the generic `Dimensions`/`buildVerifierId` design suggests is architecturally supported), the exploit is straightforward, cheap, and fully repeatable by any unprivileged user.

### Recommendation
Do not validate token-slot balances purely via independent `balanceOf` snapshots per address. Either (a) restrict swap-type external actions to `tokenNumber == 2` at the contract level (reject any `Dimensions.tokenNumber` other than the exact count the external action consumes), or (b) have `ExternalActionSwap`/`Hinkal.transact` explicitly zero out / disallow `amountChanges` and UTXO creation for any `erc20TokenAddresses` index not touched by the external action, or (c) require the external action to declare which token indices it "owns" and force `balanceDif == 0` (with `amountChanges == 0` and no UTXO minted) for all other indices, closing the path where an untouched index's balance movement can be attributed to an attacker-controlled mirrored token.

### Proof of Concept
Foundry test plan:
1. Deploy `TokenA` (real ERC20, used as LiFi swap output) and `TokenB` (a "mirror" ERC20 whose `balanceOf(address who)` returns `TokenA.balanceOf(who)`, with a no-op/absent independent transfer path).
2. Deploy a mock LiFi router that, on `callRouter`, transfers `X` `TokenA` to the caller in exchange for the input token.
3. Register (as test admin, simulating deployed config) a verifier for `Dimensions{tokenNumber: 3, ...}` + swap `externalActionId`, and craft `circomData` with `erc20TokenAddresses = [inputToken, TokenA, TokenB]`, `amountChanges = [-inputAmount, 0, X]`, generate a matching proof (satisfying `inTotal + amountChanges[i] === outTotal` per slot and `distinctErc20AddressChecks`, which passes since `TokenA != TokenB` addresses).
4. Call `Hinkal.transact`.
5. Assert: `TokenA.balanceOf(hinkal) - oldBalanceA == X` (real value received once) while the minted shielded value equals `utxoAmount(A) + amountChanges[TokenB] == 2X`, i.e., `netRealValueIn (X) < mintedShieldedValue (2X)` - confirming the invariant `net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts)` is violated.

### Citations

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

**File:** contracts/Hinkal.sol (L97-146)
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
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L40-102)
```text
    function swap(
        CircomData calldata circomData,
        int256[] calldata deltaAmounts
    ) internal returns (UTXO[] memory utxoSet) {
        address inputToken = circomData.erc20TokenAddresses[0];
        uint256 inputAmount = uint256(-deltaAmounts[0]);

        if (inputToken == circomData.feeStructure.feeToken) {
            inputAmount -= circomData.feeStructure.flatFee;
        }

        address outputToken = circomData.erc20TokenAddresses[1];

        require(
            circomData.slippageValues[1] != 0,
            "swap output slippage floor not set"
        );

        require(
            block.timestamp <= circomData.timeStamp + SWAP_DEADLINE_WINDOW,
            "swap expired"
        );

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
    }
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

**File:** contracts/external-actions/swaps/LifiExternalAction.sol (L16-36)
```text
    function callRouter(
        address inputToken,
        uint256 inputAmount,
        address outputToken,
        bytes calldata externalActionMetadata
    ) internal override returns (uint256 swappedAmount) {
        uint256 balanceBefore = getERC20OrETHBalance(outputToken);

        if (inputToken == address(0)) {
            (bool success, ) = router.call{value: inputAmount}(
                externalActionMetadata
            );
            require(success, "LI.FI swap failed: native coin");
        } else {
            approveUnlimited(inputToken, router);
            (bool success, ) = router.call(externalActionMetadata);
            require(success, "LI.FI swap failed: erc-20 token");
        }

        swappedAmount = getERC20OrETHBalance(outputToken) - balanceBefore;
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
