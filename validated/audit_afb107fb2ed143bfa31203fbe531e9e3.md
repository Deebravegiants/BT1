### Title
Emporium `runAction` executes arbitrary `op.endpoint.call` unconstrained by `circomData.erc20TokenAddresses`, allowing theft of any token balance held by Emporium - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.runAction` executes attacker-supplied `EmporiumOperation.callData` against attacker-supplied `endpoint` addresses with `msg.sender == Emporium`, and the only accounting check (`balancesBefore`/`balancesAfter`/`deltaAmountChanges`) is limited to the tokens listed in `circomData.erc20TokenAddresses`. When that array is empty (as selected via `CircomDataBuilder.formInputForCircom`'s `formInputEmporiumMin` branch), no balance conservation check exists at all for a call that transfers out any pre-existing token balance sitting at the Emporium address.

### Finding Description
The broken equality is the value-conservation check in `Hinkal.transact`:
```
balanceDif == (onChainCreation[i] ? 0 : amountChanges[i]) + utxoAmount
``` [1](#0-0) 
This is only evaluated per-index over `circomData.erc20TokenAddresses` [2](#0-1) . When `circomData.erc20TokenAddresses.length == 0`, this loop body never executes for any token — the equality is vacuously never checked, for any asset.

Inside `EmporiumUpgradeable.runAction`, the same restriction applies to the internal balance snapshot/utxo logic: `balancesBefore`/`balancesAfter` are computed only `getBalancesForArray(circomData.erc20TokenAddresses)` [3](#0-2) , and the subsequent `balanceChange`/`handleOut` conservation logic only loops over `circomData.erc20TokenAddresses` [4](#0-3) . But critically, the actual arbitrary call execution loop over `stack.ops` — `op.endpoint.call{value: op.value}(op.callData)` — is **not gated by `erc20TokenAddresses` at all**; it runs unconditionally for every op in the stack, regardless of the array's contents or length [5](#0-4) . The only gate on `runAction` is `onlyAllowedRecipient`, which merely checks `msg.sender == Hinkal` (i.e., that the call came from the Hinkal contract, not that the payload/endpoints are safe) [6](#0-5) . `verifyWallet` only checks `usedMessages[emporiumMessage]` and, when `signerAddress == address(0)`, returns immediately without any signature or asset check [7](#0-6) .

The `formInputEmporiumMin` circuit-input path only feeds `[emporiumMessage, timeStamp, calldataHash]` to the proof system [8](#0-7) , selected whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0` [9](#0-8) . This minimal circuit does not constrain `op.endpoint` or `op.callData` at all — those come from `externalActionData.externalActionMetadata`, which is plain calldata decoded directly by `runAction` with no circuit-level or on-chain-level restriction on which contract/method is called.

Attacker flow: submit `transact` with the min-circuit dimensions, `erc20TokenAddresses = []`, and `externalActionMetadata` encoding an `EmporiumStack` with `signerAddress = address(0)` and one op targeting `WETH.transfer(attacker, dustBalance)`. Since `erc20TokenAddresses` is empty:
- `Hinkal.transact`'s balance-conservation loop never runs — no check on WETH moved.
- `_externalTransact`'s `deltaAmountChanges` array is empty, so no negative-transfer-in guard applies either.
- Inside `runAction`, the `stack.ops` loop executes the WETH transfer unconditionally, moving Emporium's WETH balance to the attacker.
- `verifyWallet` passes trivially (no signature required since `signerAddress == address(0)`, only a fresh, attacker-chosen `emporiumMessage` needs to not be previously used).
- No later loop iterates over `erc20TokenAddresses` (it's empty) so `handleOut`/balance-diff logic never inspects WETH.

This works for **any leftover token balance** at the Emporium address, not just from the specific "leftover dust" precondition described in the prompt — any prior legitimate Emporium interaction that leaves a residual token balance (which is architecturally possible any time a token isn't fully swept back via `handleOut`, e.g., due to rounding, partial swaps, or a token not included in a prior transaction's `erc20TokenAddresses` list) becomes stealable by any subsequent unprivileged caller.

### Impact Explanation
Direct theft of ERC20 (or ETH) balances resident at the Emporium contract, which belong to whichever depositor's action left them there. Since `Emporium` acts with its own identity (`msg.sender == Emporium`) when performing `op.endpoint.call`, and there is no restriction tying `op.endpoint`/`op.callData` to the tracked `erc20TokenAddresses`/`amountChanges`, this is a full bypass of value conservation — matching "Critical: direct theft of shielded or in-flight user funds." It is repeatable: any attacker can call `transact` repeatedly (choosing a fresh `emporiumMessage` each time) to drain any token balance that accumulates at Emporium.

### Likelihood Explanation
Precondition: Emporium must hold a nonzero balance of some ERC20/ETH not currently claimed via an in-flight `erc20TokenAddresses` accounting. Given the architecture (`handleOut` only sweeps for `balanceChange > 0`, and dust/rounding is common with swap-like ops), this state is plausible over time. Attacker cost is minimal — a single `transact` call with a locally computed `messageSeed` satisfying `Poseidon(1)([messageSeed]) == emporiumMessage`, using the min-circuit verifier which only constrains `emporiumMessage`, `timeStamp`, `calldataHash`. No proof-of-ownership of the drained funds, no privileged role, no relayer collusion needed. This is fully within the stated "unprivileged EOA" attacker model.

### Recommendation
Do not allow `formInputEmporiumMin`/empty `erc20TokenAddresses` to bypass balance accounting when `EmporiumOperation`s can call arbitrary endpoints. Either: (1) require that every token touched by any `op.endpoint.call` in the stack be present in `circomData.erc20TokenAddresses` and enforce the conservation equation over exactly that set (e.g., by whitelisting/declaring touched tokens in the metadata and validating post-hoc balances for all of them, not just a caller-chosen subset), or (2) restrict `op.endpoint` calls to a strict allow-list of vetted protocols/methods that cannot move Emporium's own token balances to arbitrary third parties, or (3) sweep/zero out Emporium's balance for every token acted upon within the same transaction regardless of whether it's declared in `erc20TokenAddresses`, and revert if any undeclared token balance changed.

### Proof of Concept
Foundry fork test:
1. Deploy/fork Hinkal + Emporium; perform one legitimate Emporium `transact` (with correct `erc20TokenAddresses` including WETH) whose op leaves residual WETH at Emporium (e.g., a swap op that receives slightly more WETH than accounted for, or simply an ETH deposit that isn't fully claimed) — assert `WETH.balanceOf(Emporium) > 0` afterward.
2. Off-chain, brute force / compute `messageSeed` such that `Poseidon(1)([messageSeed]) == emporiumMessage` for an unused `emporiumMessage`; generate a valid snarkjs proof for `MainEVMCircuitMin` with public inputs `[emporiumMessage, timeStamp, calldataHash]`.
3. Call `Hinkal.transact` with `dimensions` selecting the min circuit, `circomData.erc20TokenAddresses = []`, `circomData.externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, and `externalActionMetadata` encoding `EmporiumStack{signerAddress: address(0), ops: [EmporiumOperation{endpoint: WETH, invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC20.transfer.selector, attacker, dustBalance)}], maxFee: 0, deadline: 0, v/r/s: 0}`.
4. Assert `WETH.balanceOf(attacker)` increased by `dustBalance` and `WETH.balanceOf(Emporium)` decreased by the same, while `circomData.erc20TokenAddresses.length == 0` throughout, and that `Hinkal.transact`'s conservation `require` at [10](#0-9)  was never evaluated for WETH (loop bound is 0).

### Citations

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-87)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L91-118)
```text
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-151)
```text
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

**File:** contracts/CircomDataBuilder.sol (L139-148)
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
```

**File:** contracts/CircomDataBuilder.sol (L150-161)
```text
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
