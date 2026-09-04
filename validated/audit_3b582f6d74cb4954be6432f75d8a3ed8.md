## Finding [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Residual/stranded token balances in `EmporiumUpgradeable` can be swept by any caller when the swept token is excluded from `circomData.erc20TokenAddresses` — (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` only measures balance changes for the tokens the attacker chooses to list in `circomData.erc20TokenAddresses`, and lets each `EmporiumOperation` make an arbitrary, unconstrained external call (`op.endpoint.call{value: op.value}(op.callData)`). Any ERC20/ETH balance sitting in the Emporium contract that is not one of the declared tokens for the current call — whether it is a router refund, an intermediate-hop token, or dust left by a prior action — is invisible to every accounting check and can be moved by an arbitrary call into a declared output token (or transferred out directly), where it is credited to the caller as their own UTXO or sent straight to their EOA.

### Finding Description
The invariant the protocol expects is: *tokens leaving an action in a tx == -deltaAmountChanges Hinkal sent it that tx*. This is enforced only per index of `circomData.erc20TokenAddresses`:

- In `Hinkal._externalTransact`, Hinkal transfers `-deltaAmountChanges[i]` into the action only for `i` in `circomData.erc20TokenAddresses` [4](#0-3) .
- In `EmporiumUpgradeable.runAction`, `balancesBefore`/`balancesAfter` are captured only for `circomData.erc20TokenAddresses`, and the correction `balanceChange -= deltaAmountChanges[i]` (adding back what was deposited) only reconciles those same indices [5](#0-4) .
- `Hinkal.transact`'s post-action balance-diff/slippage checks likewise only iterate `circomData.erc20TokenAddresses` [6](#0-5) .

Crucially, `circomData.erc20TokenAddresses` is entirely attacker-chosen — `dimensionsCheck` only requires internal-array-length consistency, not that it covers every token the action might ever touch [7](#0-6) . In the extreme, `CircomDataBuilder.formInputForCircom` has a dedicated path, `formInputEmporiumMin`, used whenever `circomData.erc20TokenAddresses.length == 0` for the Emporium action, which encodes only `emporiumMessage`, `timeStamp`, and `calldataHash` as public circuit inputs — no token, no amount, no nullifier, no output-commitment signals are constrained at all [8](#0-7) . With zero tokens declared, `runAction`'s balancesBefore/After loop and Hinkal's post-action balance-diff loop both run zero iterations, so absolutely no economic check applies to that call.

Meanwhile, `EmporiumOperation`s in "Stateless Interaction" mode allow calling **any** `op.endpoint` with **any** `op.callData` and value, the only restriction being that the call is not `IHinkalWallet.callHinkalWallet`/`doSendToRelay` [9](#0-8) . No signature is required when `stack.signerAddress == address(0)`; only the `usedMessages[circomData.emporiumMessage]` replay guard applies, which the attacker trivially satisfies with a fresh nonce [10](#0-9) .

Consequently, an attacker can:
1. Craft `circomData` for the Emporium action with `erc20TokenAddresses = []` (or excluding the target token while including some legitimate output token), a trivially valid ZK proof (a tree with a single existing leaf suffices for `rootHashHinkal`/`rootHashHinkalIndex` since with `tokenCount = 0` no merkle/nullifier constraints exist in the circuit at all), and an `EmporiumStack` whose `ops` call `TargetToken.transfer(attackerEOA, TargetToken.balanceOf(emporium))` (or route the balance through a DEX into a declared output token).
2. Call `Hinkal.transact` — `performHinkalChecks`/`dimensionsCheck`/`verifyProof`/`rootHashExists` all pass because nothing constrains the stateless op calls or the swept token.
3. `EmporiumUpgradeable.runAction` executes the op, transferring the entire stranded/residual balance of `TargetToken` to the attacker (directly, or laundered into a declared output token and returned via `handleOut` as the attacker's own UTXO).

None of the existing guards catch this because they are all scoped to `circomData.erc20TokenAddresses`: the `BalanceChangeShouldBePositive` revert in `handleOut`'s caller loop [11](#0-10)  never fires for a token that is not in that array; `onlyAllowedRecipient` only checks that the caller is Hinkal itself [12](#0-11) ; and `verifyWallet`'s EIP-712 signature check is entirely skipped when `signerAddress == address(0)`.

### Impact Explanation
Direct theft of protocol/in-flight funds: any ERC20 or ETH balance that ends up parked in the shared, singleton `EmporiumUpgradeable` contract (via router refunds, partial fills, dust from intermediate swap legs, or any prior user's transaction that didn't fully account for a token) is drainable by any unprivileged, unrelated caller to their own address or their own shielded UTXO — with no proof of ownership of that value ever required. This matches Critical: "direct theft of shielded or in-flight user funds." It is fully repeatable for every future occurrence of a stranded balance and is not limited to funds the attacker deposited.

### Likelihood Explanation
- Preconditions: some non-zero ERC20/ETH balance exists in the Emporium contract that is not part of the current `erc20TokenAddresses` set (easily produced by normal multi-hop swap ops, partial-fill router refunds landing on an intermediate token, or simply a prior transaction that omitted a token from its declared set).
- Attacker cost: only gas plus a trivially constructible proof — a tree with a single existing leaf/root is sufficient, and with `erc20TokenAddresses.length == 0` no nullifier/UTXO constraints exist at all in the circuit's public inputs.
- No privileged role, whitelisted relay, or victim cooperation is required — this is reachable by any EOA through `Hinkal.transact`.
- Repeatable indefinitely as long as any stray balance accumulates in the Emporium contract.

### Recommendation
Track and reconcile the Emporium contract's balance for every token that any `EmporiumOperation` interacts with, not only the caller-declared `circomData.erc20TokenAddresses`. Concretely: (1) disallow `erc20TokenAddresses.length == 0` for the Emporium action, or require declared tokens to encompass all tokens the ops can touch, e.g. by whitelisting/validating `op.endpoint` and decoding the tokens involved; (2) enforce a strict "no un-tracked token balance may decrease" invariant across the whole call, not just declared indices — e.g., snapshot balances for a fixed/registered token allowlist, or require the action to hold zero balance of any non-declared token before and after each call; (3) require a valid EIP-712 signed operation stack for the stateless path as well, so an attacker cannot author arbitrary `ops` for an action instance shared with other users' residual value.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (registered as `HINKAL_EMPORIUM_ACTION_ID`) with `Hinkal` as an allowed recipient.
2. Seed a residual balance: transfer `TOKEN_A` directly to the deployed `EmporiumUpgradeable` address (simulating a router refund / stranded balance from an unrelated prior action) — assert `TOKEN_A.balanceOf(emporium) == R > 0`.
3. Make one legitimate Hinkal deposit so the Merkle tree has exactly one leaf (`roots[MINIMUM_INDEX]` = that leaf), to obtain a valid `rootHashHinkal`.
4. As an unrelated attacker EOA, build `circomData` with `erc20TokenAddresses = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionMetadata` = ABI-encoded `EmporiumStack{ signerAddress: address(0), ops: [ EmporiumOperation{ endpoint: TOKEN_A, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, R)) } ] }`, and generate the corresponding trivial proof via `formInputEmporiumMin`.
5. Call `Hinkal.transact(a, b, c, dimensions, circomData)` from the attacker.
6. Assert: before tx, `TOKEN_A.balanceOf(emporium) == R` and `TOKEN_A.balanceOf(attacker) == 0`; after tx, `TOKEN_A.balanceOf(emporium) == 0` and `TOKEN_A.balanceOf(attacker) == R`, while `deltaAmountChanges` computed/sent by Hinkal for this tx was `0` (empty array) — demonstrating tokens left the action with no corresponding `-deltaAmountChanges` from Hinkal, breaking the claimed invariant.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-160)
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-317)
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

**File:** contracts/CircomDataBuilder.sol (L134-161)
```text
    function formInputForCircom(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory) {
        if (
            circomData.externalActionData.externalActionId ==
            HINKAL_EMPORIUM_ACTION_ID &&
            circomData.erc20TokenAddresses.length == 0
        ) {
            return formInputEmporiumMin(circomData);
        } else {
            return formInputNormal(chainId, verifyingContract, circomData);
        }
    }

    function formInputEmporiumMin(
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory input) {
        input = new uint256[](circomData.publicSignalCount);

        uint16 index = 0;

        input[index++] = circomData.emporiumMessage;

        input[index++] = circomData.timeStamp;
        input[index++] = circomData.calldataHash;
    }
```

**File:** contracts/HinkalHelper.sol (L64-105)
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

**File:** contracts/external-actions/ExternalActionBaseUpgradeable.sol (L39-46)
```text
    modifier onlyAllowedRecipient() {
        ExternalActionBaseStorage storage $ = _getExternalActionBaseStorage();
        require(
            $._isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }
```
