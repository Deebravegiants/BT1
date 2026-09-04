## Analysis

The claimed broken equality is: **real value entering the vault == sum(amountChanges) + sum(on-chain UTXO amounts)**, per `Hinkal.transact`'s per-index check [1](#0-0) . I traced this and confirmed the divergence is real for internal transacts (`externalActionId == 0`).

### Root cause

`Hinkal.transact` snapshots balances **per array index**, not per unique token, via `getBalancesForArray` calling `balanceOf` on each `erc20TokenAddresses[i]` independently [2](#0-1) . The subsequent check loop verifies `balanceDif == amountChanges[i] + utxoAmount` **independently for each index `i`** [3](#0-2) , with no cross-index deduplication of the *economic* balance being measured.

The only anti-duplication guard is inside the circuit, which forces `erc20TokenAddresses[i] != erc20TokenAddresses[j]` as raw field elements [4](#0-3) . This only prevents literal address duplication — it cannot and does not detect that two *different* attacker-deployed contract addresses `A` and `B` expose the *same* underlying balance (e.g., `B.balanceOf()` simply forwards to/reads `A`'s balance of the vault).

For internal transacts, `checkOnchainCreation` forces `onChainCreation[i] == false` for all indices [5](#0-4) , and `_internalTransact` performs the actual token movement per index using `_calculateDeltaAmount`, calling `transferERC20TokenFromOrCheckETH`/`transferERC20TokenOrETH` on whatever address `erc20TokenAddresses[i]` is — entirely attacker-controlled contract code [6](#0-5) .

### Exploit flow

1. Attacker deploys two contracts, `A` (a real ERC20) and `B`, where `B.balanceOf(vault)` is coded to mirror/forward to `A.balanceOf(vault)`, but `B.transferFrom(...)` is a no-op (returns `true`, moves nothing).
2. Attacker calls `transact` with `erc20TokenAddresses = [A, B]`, `amountChanges = [X, X]`, `onChainCreation = [false, false]`, matched proof/output commitments for both indices.
3. `_internalTransact` loop: index 0 does a real `A.transferFrom(sender, vault, X)`, genuinely raising `A`'s real balance held by vault by `X`. Index 1 calls `B.transferFrom(sender, vault, X)`, a no-op.
4. In the post-check loop, `newBalances[1] - oldBalances[1]` still equals `X` because `B.balanceOf` mirrors `A`'s balance, which really did increase by `X` in step 3. So `balanceDif[1] == amountChanges[1] (X) + utxoAmount(0)` holds — the check for index 1 passes despite no real deposit of `B`.
5. The circuit's internal constraint `inTotal + amountChanges[i] === outTotal` is satisfied for index 1 regardless of real-world backing (it only checks internal consistency of `amountChanges` vs private output amounts), so a valid shielded output commitment for "token `B`" worth `X` is inserted into the merkle tree via `insertCommitments` [7](#0-6) .

Net result: the vault received `X` of real assets once, but two independently-spendable shielded UTXO balances worth `X` each now exist (`A`: `X`, `B`: `X`), one of which is entirely unbacked. Redeeming both later withdraws `2X` of real value for `X` deposited, producing protocol insolvency — minting shielded value without backing.

### Why existing guards fail
`performHinkalChecks`, `dimensionsCheck`, and `checkOnchainCreation` only validate array-length/flag consistency, not economic uniqueness of the addresses [8](#0-7) . `verifyProof`/circuit's `distinctErc20AddressChecks` only forbids literal address collisions, not balance aliasing, since circom has no way to inspect `balanceOf` semantics [4](#0-3) . Hinkal has no on-chain token allow-list/registry restricting which ERC20 addresses can be used in `erc20TokenAddresses`.

### Title
Minting unbacked shielded value via aliased/"double-entry" token addresses in internal transact - (File: contracts/Hinkal.sol)

### Summary
`Hinkal.transact`'s balance-diff check is computed independently per array index of `erc20TokenAddresses` using raw `balanceOf` snapshots, without verifying the addresses represent economically distinct balances. An attacker who deploys a token pair `(A, B)` where `B.balanceOf()` mirrors `A`'s real balance but `B.transferFrom()` is a no-op can pass the on-chain equality check for both indices while only depositing real value once, minting a fully unbacked shielded UTXO for token `B`.

### Finding Description
The broken equality: `balanceDif[i] == amountChanges[i] + utxoAmount[i]` is checked per-index over `erc20TokenAddresses`, computed via independent `balanceOf` calls per address [9](#0-8) . Nothing enforces that the addresses in this array correspond to economically independent token balances — only literal address-value distinctness is enforced in the circuit [4](#0-3) . An attacker deploys `A` (real ERC20) and `B` (a contract whose `balanceOf(vault)` mirrors `A`'s balance of the vault, and whose `transferFrom` is a no-op). In one `transact` call with `externalActionId == 0`, `_internalTransact` [6](#0-5)  performs a real deposit of `X` via `A` and a fake no-op "deposit" via `B`. Because `B`'s reported balance moves in lockstep with `A`'s real balance, the post-check for `B`'s index is satisfied despite no real value transfer, and a shielded UTXO of `X` for token `B` gets committed to the tree, unbacked by any real asset.

### Impact Explanation
The attacker mints shielded UTXO value for token `B` with zero real backing, while only ever depositing `X` real tokens (via `A`). Redeeming both the `A`-UTXO and the unbacked `B`-UTXO drains `2X` from the vault against a single `X` deposit — direct protocol insolvency / minting shielded value without backing, matching Critical severity. This is repeatable per attacker-deployed token pair and per deposit amount, with no cap other than gas/array-length limits.

### Likelihood Explanation
No privileged role is required. The attacker only needs to deploy two contracts they fully control and generate their own valid proof/circuit inputs for a legitimate-looking internal transact with two token entries — well within the stated attacker capabilities. Cost is limited to gas and deployment of two simple contracts; the attack is fully deterministic and repeatable.

### Recommendation
Enforce economic uniqueness, not just address-literal uniqueness, of tokens used in a single `transact` call — e.g., require `erc20TokenAddresses` be drawn from a protocol-maintained allow-list/registry of vetted ERC20 contracts, or restructure the balance check to aggregate real balance changes per canonical token identity rather than trusting each listed address's self-reported `balanceOf` independently.

### Proof of Concept
Foundry test plan:
1. Deploy real ERC20 `TokenA`. Deploy `TokenB` whose `balanceOf(vault)` calls `TokenA.balanceOf(vault)` and whose `transferFrom`/`transfer` are no-ops returning `true`.
2. Fund attacker with `X` of `TokenA`; approve Hinkal.
3. Build `CircomData` with `erc20TokenAddresses = [TokenA, TokenB]`, `amountChanges = [X, X]`, `onChainCreation = [false, false]`, matching valid nullifiers/commitments/proof for a locally-generated circuit run satisfying `inTotal + amountChanges[i] === outTotal` for both indices.
4. Call `Hinkal.transact(...)`, assert it does not revert.
5. Assert `TokenA.balanceOf(vault)` increased by exactly `X` (real value received == `X`), while the sum of newly inserted shielded UTXO commitments' claimed value across both indices == `2X`. Assert `X (received) < 2X (credited)`, demonstrating the broken invariant `net tokens entering Hinkal == sum(amountChanges) + sum(minted UTXO amounts)`.

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

**File:** contracts/Hinkal.sol (L156-166)
```text
            insertNullifiers(
                circomData.inputNullifiers,
                circomData.onChainCreation
            );

            insertCommitments(
                circomData.outCommitments,
                circomData.encryptedOutputs,
                onChainCommitments,
                circomData.onChainCreation
            );
```

**File:** contracts/Hinkal.sol (L172-230)
```text
    function _internalTransact(CircomData calldata circomData) private {
        bool hasPaidToRelay = false;
        for (uint64 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 deltaAmountChange = _calculateDeltaAmount(circomData, i);

            if (deltaAmountChange > 0) {
                require(
                    circomData.externalActionData.externalAddress == msg.sender,
                    "Deposit should come from the sender"
                );
                transferERC20TokenFromOrCheckETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    address(this),
                    uint256(circomData.amountChanges[i])
                );
            } else {
                uint256 sumAbs = uint256(-deltaAmountChange);
                uint256 relayFee = 0;
                if (circomData.relay != address(0)) {
                    uint256 flatFee = circomData.feeStructure.feeToken ==
                        circomData.erc20TokenAddresses[i]
                        ? circomData.feeStructure.flatFee
                        : 0;

                    require(
                        sumAbs >= flatFee,
                        "Relay Fee is over withdraw amount"
                    );

                    uint256 recipientAmount = ((10000 -
                        circomData.feeStructure.variableRate) *
                        (sumAbs - flatFee)) / 10000;

                    relayFee = sumAbs - recipientAmount;

                    if (relayFee > 0) {
                        transferERC20TokenOrETH(
                            circomData.erc20TokenAddresses[i],
                            circomData.relay,
                            relayFee
                        );
                    }
                    hasPaidToRelay = true;
                }
                if (sumAbs - relayFee > 0) {
                    transferERC20TokenOrETH(
                        circomData.erc20TokenAddresses[i],
                        circomData.externalActionData.externalAddress,
                        sumAbs - relayFee
                    );
                }
            }
        }
        require(
            circomData.relay == address(0) || hasPaidToRelay,
            "relay not paid"
        );
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
