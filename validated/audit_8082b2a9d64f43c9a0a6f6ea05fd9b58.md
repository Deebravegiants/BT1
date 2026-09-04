### Title
Emporium's per-call `balancesBefore` baseline lets unlisted-token dust be drained by any later `transact()` caller via arbitrary `EmporiumOperation` calls - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` only measures balance changes for tokens present in the *caller's own* `circomData.erc20TokenAddresses` array, snapshotting `balancesBefore`/`balancesAfter` fresh on every call. Any residual token balance left on the Emporium contract by a prior user's transaction (e.g. a swap-router refund of a token that victim never listed) is invisible to that victim's accounting and is never converted into their UTXO, but sits in the contract as raw, unattributed balance that any subsequent unprivileged caller can sweep via a crafted stateless `EmporiumOperation`.

### Finding Description
The claimed equality is: `dust/refund created during victim's tx == credited to victim's own UTXO set`. In `EmporiumUpgradeable.runAction` ( [1](#0-0) ), `balancesBefore`/`balancesAfter` are computed only over `circomData.erc20TokenAddresses`, i.e. the tokens the victim's own circuit/proof explicitly lists. If a router or endpoint the victim calls sends a refund of a token not listed there directly to `address(this)` (Emporium), that inflow is never read by `getBalancesForArray`, never enters `balanceChange`, and `handleOut` is never invoked for it — so the equality is already broken for the victim: the dust is not credited to them, and no error is raised because none of `Hinkal.transact`'s slippage/balance checks touch that token either (they too iterate only `circomData.erc20TokenAddresses`, see [2](#0-1) ). The token balance is left sitting on the Emporium contract, unaccounted for by any circuit constraint, nullifier, or UTXO.

The exploitable half of the finding is what happens to that stranded balance next. `EmporiumUpgradeable.runAction`'s op-execution loop performs, for "Stateless Interaction" ops, an entirely arbitrary low-level call:
```
(success, err) = op.endpoint.call{value: op.value}(op.callData);
``` [3](#0-2) 
The only restriction is blocking the `callHinkalWallet`/`doSendToRelay` selectors; `op.endpoint` and the rest of `op.callData` are fully attacker-controlled and unconstrained by `dimensionsCheck`/`performHinkalChecks` ( [4](#0-3) ), which validate array-length/dimension consistency but never inspect `externalActionMetadata` semantics. This op is executed with `msg.sender == Emporium`, so an attacker can set `op.endpoint = <dustTokenAddress>` and `op.callData = abi.encodeWithSelector(IERC20.transfer.selector, attackerAddress, dustAmount)` to move the stranded token balance out of Emporium directly, entirely bypassing the `balancesBefore/After`/`handleOut`/UTXO pipeline (since the attacker need not even list that token in their own `erc20TokenAddresses`).

Furthermore, `verifyWallet` requires an EIP-712 signature only when `stack.signerAddress != address(0)`; when `stack.signerAddress == address(0)` it only marks the message used and returns ( [5](#0-4) ), so no counterparty signature is needed for the attacker's own crafted stack — they fully control the ops for their own `transact()` call.

### Impact Explanation
Any ERC20/ETH balance stranded on the Emporium contract by another user's action (refunds, overpayments, dust from swap routers, or any other case where an inflow isn't reflected in the caller's own `erc20TokenAddresses`) can be stolen outright by any unprivileged attacker's subsequent `transact()` call, via a direct low-level `transfer`/`call` executed with Emporium as `msg.sender`. This is direct theft of another user's (victim's) in-flight funds with no shielded accounting, matching the Critical severity bar. It is repeatable for every occurrence of unaccounted residual balance and requires no privileged role.

### Likelihood Explanation
Preconditions: (1) some legitimate flow through Emporium (e.g. a swap via a hook/endpoint called from an op) causes a residual balance of a token not included in the caller's `erc20TokenAddresses` to remain on the Emporium contract, and (2) an attacker submits any valid `transact()` with `externalActionId` pointing at Emporium, `stack.signerAddress = address(0)` (no signature required), and one stateless op targeting the dust token's `transfer` function. Both preconditions are attacker-affordable and require only standard proof generation for the attacker's own legitimate UTXOs; no owner/relay/admin role is needed.

### Recommendation
Do not allow arbitrary `op.endpoint`/`op.callData` combinations to target ERC20 token contracts (or any address) outside an allow-list of intended swap/router endpoints; alternatively, restrict "Stateless Interaction" calls to a registered allow-list of external endpoints, and/or sweep all leftover ERC20/ETH balances belonging to *all* tokens actually touched during the call (not merely those the caller chose to list) into the caller's own UTXO/slippage accounting so nothing is ever strandable on the Emporium contract.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, and a mock ERC20 "DustToken".
2. Simulate a victim transaction: have the victim's op call a mock router that, mid-call, sends `DustToken` directly to the Emporium contract (simulating an unexpected refund), while the victim's `circomData.erc20TokenAddresses` does not include `DustToken`. Assert `DustToken.balanceOf(emporium) == dustAmount` after the victim's `transact()` completes, and that no UTXO/commitment for `DustToken` was created for the victim (equality broken: dust not credited to victim).
3. As a distinct attacker, submit a second `transact()` to Emporium with `stack.signerAddress = address(0)` and a single stateless `EmporiumOperation` where `endpoint = DustToken`, `callData = abi.encodeWithSelector(IERC20.transfer.selector, attacker, dustAmount)`, and the attacker's own `erc20TokenAddresses` not necessarily including `DustToken`.
4. Assert `DustToken.balanceOf(attacker) == dustAmount` and `DustToken.balanceOf(emporium) == 0` after the attacker's call succeeds, proving the dust — created during the victim's tx and never credited to the victim's UTXO set — was captured by an unrelated later caller.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-151)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-316)
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
