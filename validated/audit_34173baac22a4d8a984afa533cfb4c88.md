### Title
Emporium can be drained of any ERC20 token balance not listed in `circomData.erc20TokenAddresses` - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.runAction` and `Hinkal.transact` only track and reconcile balances for tokens present in `circomData.erc20TokenAddresses`. Since `EmporiumOperation.endpoint`/`callData` inside `stack.ops[]` are fully attacker-controlled and unconstrained beyond a hash-commitment the attacker himself builds, an unprivileged user can add an operation that calls `T.transfer(attacker, T.balanceOf(Emporium))` for any token `T` that Emporium happens to hold but that is absent from the current transaction's `erc20TokenAddresses` array, stealing that balance with zero accounting.

### Finding Description
Broken equality: tokens leaving Emporium for token `T` should equal `-deltaAmountChanges[T]` (funds deposited for this flow) plus any pre-existing dust that the code explicitly tolerates via `balanceChange < 0` handling in `EmporiumUpgradeable.runAction` — but this equality is **never evaluated for `T`** if `T ∉ circomData.erc20TokenAddresses`.

Path:
- `Hinkal.transact` (`contracts/Hinkal.sol:30-150`) computes `oldBalances`/`newBalances` only via `getBalancesForArray(circomData.erc20TokenAddresses)` [1](#0-0) , and the reconciliation loop that enforces "change in balance == amountChanges + utxoAmount" iterates only over `circomData.erc20TokenAddresses` [2](#0-1) . If that array is empty (or simply omits `T`), no check touches `T` at all.
- `HinkalHelper.performHinkalChecks`/`dimensionsCheck` only requires `erc20TokenAddresses.length == dimensions.tokenNumber`; nothing forces this to be non-zero or to include every token an external action might touch [3](#0-2) .
- `CircomDataBuilder.formInputForCircom` even has a dedicated minimal path, `formInputEmporiumMin`, used whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`, which reduces the public circuit inputs to just `emporiumMessage`, `timeStamp`, `calldataHash` — no token/amount/nullifier signals at all [4](#0-3) .
- `EmporiumUpgradeable.runAction` computes `balancesBefore`/`balancesAfter` and the reconciliation loop the same way, scoped to `circomData.erc20TokenAddresses` [5](#0-4) . Inside the ops loop, an attacker-supplied stateless op executes `op.endpoint.call{value: op.value}(op.callData)` with essentially no restriction on the target or payload except blocking the wallet-only selectors [6](#0-5) .
- `verifyWallet` performs a signature check only when `stack.signerAddress != address(0)`; when the attacker sets `signerAddress = address(0)`, the function only marks the message used and returns, leaving `stack.ops[]` completely unconstrained by any authorization other than the attacker's own calldata hash commitment (which the attacker controls, since it's their own transaction) [7](#0-6) .

Exploit: attacker submits `Hinkal.transact` with `circomData.erc20TokenAddresses = []` (or any set excluding `T`), `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionMetadata` encoding an `EmporiumStack{signerAddress: address(0), ops: [{endpoint: T, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attackerEOA, T.balanceOf(Emporium)))}]}`. Because `T ∉ erc20TokenAddresses`, `T`'s outgoing transfer is invisible to every balance-diff check in both `Hinkal.transact` and `EmporiumUpgradeable.runAction`, and the call succeeds unconditionally as long as `msg.sender == Emporium` (which it is, since Emporium itself executes the `.call`).

### Impact Explanation
Any ERC20 balance the shared `Emporium` contract holds for a token not enumerated in an attacker's own `erc20TokenAddresses` array can be transferred out by that attacker with no economic cost and no proof-based constraint on the transfer. Because Emporium is a single shared contract used by all users' external-action flows, such a balance can represent dust/residue from other users' in-flight swaps (slippage remainders, rounding, fee-on-transfer tokens, or partially-swept balances from a prior transaction). This is direct, repeatable theft of value sitting in Emporium that was never counted by the protocol's value-conservation checks, matching the Critical category ("direct theft of shielded or in-flight user funds").

### Likelihood Explanation
Preconditions are modest and realistic: Emporium must hold a nonzero balance of some token `T` (which can arise from ordinary swap slippage, rounding, or fee-on-transfer tokens across the many transactions routed through the shared Emporium). The attacker needs no special privilege — they generate their own valid proof (trivially, via the Min-circuit path with zero tokens/nullifiers), and craft `circomData` fully under their control. `T.balanceOf(Emporium)` is public information, so discovering exploitable dust is straightforward and the attack is repeatable indefinitely for every accruing dust balance.

### Recommendation
Do not scope Emporium's/Hinkal's balance reconciliation to only the tokens the caller chooses to declare. Either (a) require `EmporiumOperation.endpoint`/token targets to be a subset of `circomData.erc20TokenAddresses` and reject any successful call whose resulting balance deltas touch a token outside that set, or (b) track and reconcile balances for every token actually touched by `stack.ops` (e.g., by decoding intended target tokens up front and forcing them into the checked set), so `balanceChange` accounting can never be skipped for a token because it was omitted from the declared array. Additionally, prevent `erc20TokenAddresses.length == 0` (the "Min" path) from being usable together with an Emporium action whose `ops[]` perform arbitrary token-moving calls, or restrict `op.endpoint` to a controlled allow-list of routers/tokens.

### Proof of Concept
Hardhat fork/unit test plan:
1. Deploy Hinkal + `HinkalHelper` + `EmporiumUpgradeable` per repo test harness; register Emporium under `HINKAL_EMPORIUM_ACTION_ID`.
2. Mint/transfer token `T` directly to the deployed Emporium proxy address (simulating stranded dust), record `balanceBefore = T.balanceOf(Emporium)`.
3. As an unprivileged attacker EOA, build `circomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `onChainCreation = []`, `inputNullifiers = []`, `outCommitments = []`, `externalActionData = {externalAddress: Emporium, externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalActionMetadata: abi.encode(EmporiumStack{signerAddress: address(0), ops: [{endpoint: address(T), invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, balanceBefore))}], maxFee: 0, deadline: type(uint256).max})}`.
4. Generate a locally-produced Groth16 proof for the Min circuit (`dimensions.tokenNumber = 0`, etc.) matching `formInputEmporiumMin`'s three public inputs.
5. Call `Hinkal.transact(a, b, c, dimensions, circomData)` from the attacker EOA.
6. Assert: transaction succeeds; `T.balanceOf(attacker) == balanceBefore`; `T.balanceOf(Emporium) == 0`; and that `Hinkal.transact`'s `oldBalances`/`newBalances`/`balanceDif` arrays were length-0 throughout (i.e., no equality was ever checked for `T`), while `EmporiumUpgradeable.runAction`'s `balancesBefore`/`balancesAfter` arrays were likewise empty.

### Citations

**File:** contracts/Hinkal.sol (L78-90)
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

**File:** contracts/HinkalHelper.sol (L64-90)
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
```

**File:** contracts/CircomDataBuilder.sol (L139-161)
```text
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
