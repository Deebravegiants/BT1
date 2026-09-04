### Title
Emporium mints unbacked UTXOs from tokens not declared in `circomData.erc20TokenAddresses` - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.runAction` only measures balance deltas for tokens explicitly listed in `circomData.erc20TokenAddresses`, and its `EmporiumStack.ops[]` can call arbitrary `endpoint.call(...)` (including `approve`/swap calldata against any token Emporium happens to hold). An attacker can spend a resident-but-undeclared token (e.g. dust/stray `tokenA` left on the Emporium contract) inside a stateless op, swap it into `tokenB`, and only declare `tokenB` with `deltaAmountChanges[0] == 0`, causing `handleOut` to mint a fully-backed-looking UTXO for `tokenB` whose true source value (`tokenA`) was never part of any proof or balance check.

### Finding Description
The broken equality is: value the attacker receives from Emporium (`tokenB` credited via `handleOut`) should equal `-deltaAmountChanges[tokenB]` (what Hinkal actually sent into the swap for that token). In this exploit `deltaAmountChanges[0] == 0` (attacker deposits nothing), yet `handleOut` still mints a positive UTXO because the value actually came from `tokenA`, a token that never appears anywhere in `circomData.erc20TokenAddresses`.

Code path:
- `EmporiumUpgradeable.runAction` snapshots `balancesBefore`/`balancesAfter` only for `circomData.erc20TokenAddresses` [1](#0-0) .
- The stateless op branch lets Emporium execute arbitrary calldata against any endpoint, including tokens/routers it wasn't declared to touch [2](#0-1) .
- `balanceChange` for `tokenB` is computed purely from `balancesAfter[i]-balancesBefore[i]`; since `deltaAmountChanges[i] < 0` is false (it's `0`), the subtraction branch is skipped, so the entire swap gain is treated as legitimate [3](#0-2) .
- `handleOut` unconditionally transfers `balanceChange` to `msg.sender` (Hinkal) and mints a UTXO of that amount [4](#0-3) .
- In `Hinkal.transact`, the outer balance check only iterates `circomData.erc20TokenAddresses` (i.e. just `tokenB`), and it is defined to be self-consistent with `utxoAmount` (the very UTXO Emporium just minted), so it can never detect that the UTXO's backing token (`tokenA`) never appeared in the circuit's public inputs: `balanceDif == (onChainCreation[i] ? 0 : amountChanges[i]) + utxoAmount` [5](#0-4) .
- The circuit (`MainEVMCircuit`) only constrains the declared `erc20TokenAddresses`/`amountChanges` via `inTotal + amountChanges[i] === outTotal` [6](#0-5) ; with zero declared input UTXOs (`inTotal = 0`) and `amountChanges[0] = 0`, this is trivially satisfied without proving ownership of any deposit at all. `dimensionsCheck`/`checkOnchainCreation` in `HinkalHelper.sol` only validate array-length consistency and the `onChainCreation` flag combination, not that every token touched by the Emporium ops is declared [7](#0-6) .

Root cause: there is no mechanism forcing every token balance an `EmporiumStack` op can move to be included in `circomData.erc20TokenAddresses`; only the declared token set's before/after deltas are checked, so any resident balance of an undeclared token is silently "free" collateral for whoever crafts a stack that spends it.

### Impact Explanation
An unprivileged attacker mints a shielded UTXO for `tokenB` backed by zero deposit and zero verified input, using value that actually came from `tokenA` residing on the Emporium contract (e.g., dust/rounding remainder or an unclaimed fee change from any prior user's transaction). This is unbacked minting of shielded value / theft of protocol-parked funds belonging to no declared owner, matching Critical severity. The attack is repeatable any time stray/undeclared token balance exists on the Emporium contract.

### Likelihood Explanation
Preconditions: Emporium must hold a non-zero balance of some token (`tokenA`) that is not the token declared in the current transaction. This is realistic given imprecise DEX swap outputs, slippage remainders, or fee-token change that can accumulate from ordinary usage. The attacker needs no privileged role, no ownership of any UTXO (a zero-input proof with `amountChanges = 0` suffices to satisfy the circuit), and only needs to craft an `EmporiumStack` with a stateless op(s) that approve/swap the resident `tokenA` into `tokenB` while declaring only `tokenB` in `circomData.erc20TokenAddresses`.

### Recommendation
Require every token address touched by any `EmporiumOperation` (or at minimum every token whose Emporium balance changes during `runAction`) to be present in `circomData.erc20TokenAddresses`, and enforce that Emporium's balance for every ERC20 it ever holds returns to (or below) its pre-call value for tokens not declared, e.g. by whitelisting/tracking all tokens touched during op execution and reverting if any undeclared token balance decreased, or by requiring `ops` to only interact with tokens explicitly present in the declared token set.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable`, a mock ERC20 `tokenA`, `tokenB`, and a mock swap router that swaps `tokenA -> tokenB` 1:1.
2. Simulate a "stranded remainder": directly transfer `tokenA` to the Emporium contract address (representing dust from a prior transaction), without any corresponding UTXO/commitment for it.
3. As an unprivileged EOA (no prior deposit, no owned UTXO), build a `CircomData` with `erc20TokenAddresses = [tokenB]`, `amountChanges = [0]`, zero input nullifiers, and generate a valid zero-input proof (`inTotal=0`, `outTotal=0` satisfies `inTotal + amountChanges[0] === outTotal`).
4. Encode an `EmporiumStack` whose `ops[]` (stateless, `invokeWallet=false`) call `tokenA.approve(router, strandedAmount)` then `router.swap(tokenA, tokenB, strandedAmount)`, both executed by Emporium itself.
5. Call `Hinkal.transact(...)`.
6. Assert: `tokenB` balance transferred to attacker (or minted UTXO amount) > 0, while `circomData.amountChanges[0] == 0` and no `tokenA` entry exists anywhere in `circomData.erc20TokenAddresses`/nullifiers — i.e., value received by attacker ≠ `-deltaAmountChanges[tokenB]` (which is 0), proving unbacked minting.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-124)
```text
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

        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L132-150)
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

**File:** circuits/MainEVMCircuit.circom (L149-169)
```text
        inTotal += inAmounts[i][j];
      }

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
	}
```

**File:** contracts/HinkalHelper.sol (L64-202)
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
