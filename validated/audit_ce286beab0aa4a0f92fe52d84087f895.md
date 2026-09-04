This confirms the picture: `SignatureVerifier.circom` only verifies the EdDSA signature over `signedMessageHash` (the note/UTXO-spend authorization), and has no notion of `op.endpoint`/`callData` semantics at all — it never constrains what the Emporium's ops actually do. The binding of `externalActionMetadata` (which contains the `EmporiumStack.ops`) into the proof only happens through `calldataHash`/`getHashedCalldata1` in `contracts/CircomDataBuilder.sol`, which merely hashes `externalActionData` (including the metadata) to make sure the calldata the relayer submits matches what the prover intended — it does not restrict `op.endpoint` to be one of `circomData.erc20TokenAddresses`, nor does it constrain the total value that can be moved by the ops. [1](#0-0) 

## Title
Unrestricted `EmporiumOperation.endpoint.call` drains any ERC20 balance held by Emporium when it is not listed in `circomData.erc20TokenAddresses` - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` executes every attacker-supplied `EmporiumOperation` via a raw `op.endpoint.call{value: op.value}(op.callData)` in the "stateless" branch, with the only guard being a selector blacklist for `callHinkalWallet`/`doSendToRelay`. The post-call accounting (the only invariant enforced) iterates solely over `circomData.erc20TokenAddresses`, an attacker-chosen array that can be set to length 0 (or simply omit the targeted token), so calls that move tokens not listed there are never balance-checked, letting the attacker sweep any ERC20 balance sitting on the Emporium contract to themselves in a single `transact` call.

### Finding Description
The broken equality: **assets Emporium can move in the transaction (union over `op.endpoint.call` targets in `stack.ops`) != assets accounted for by `circomData.erc20TokenAddresses`** (which the attacker controls and can set to `[]`).

Path: an unprivileged attacker calls `Hinkal.transact()` with `externalActionData.externalActionId` = the registered Emporium id, `externalActionData.externalActionMetadata` = an ABI-encoded `EmporiumStack` whose `ops` array contains N entries, each `op.endpoint` = a different ERC20 token address that Emporium happens to hold a balance of, `op.callData` = `IERC20.transfer(attacker, balanceOf(Emporium))`, `op.invokeWallet = false`, and `stack.signerAddress = address(0)` (so `verifyWallet` at [2](#0-1)  returns immediately without requiring any signature). The attacker also sets `circomData.erc20TokenAddresses = []` (min-circuit path), which is legal per `formInputForCircom`/`formInputEmporiumMin` [3](#0-2) , which only commits `emporiumMessage`, `timeStamp`, and `calldataHash` as public signals — no signal ties `op.endpoint`/`op.callData` semantics to anything the circuit constrains, and `SignatureVerifier.circom` only checks the EdDSA note-spend signature, not the op contents.

Inside `runAction`, `balancesBefore`/`balancesAfter` are computed only over `circomData.erc20TokenAddresses` [4](#0-3)  and [5](#0-4) , and with length 0 the reconciliation loop at lines 132-151 never executes, so `BalanceChangeShouldBePositive` can never fire for the drained tokens. The `ops` loop itself performs the calls unconditionally: [6](#0-5) . `Hinkal.sol::transact`'s own balance-diff check (`balanceDif == amountChanges[i] + utxoAmount`) is likewise only computed per `circomData.erc20TokenAddresses` [7](#0-6) , so it provides no protection either. `onlyAllowedRecipient` only checks that the caller of `runAction` is Hinkal itself (a legitimate configuration), it does not constrain `op.endpoint`.

Even with `erc20TokenAddresses.length > 0`, the same flaw generalizes: the attacker can list unrelated/dummy tokens with zero `amountChanges`/`slippageValues` to satisfy the reconciliation loop trivially while `op.endpoint` targets a completely different, unlisted token that Emporium holds — the loop never cross-checks that `op.endpoint` is restricted to the listed set.

### Impact Explanation
Any ERC20 (or ETH) balance sitting on the Emporium contract — funds legitimately parked there mid-flow by any number of prior users (e.g., deposits awaiting a swap leg, un-forwarded outputs, dust) — can be swept to an attacker in a single transaction with no signature and no on-chain balance check preventing it. This is direct, unauthorized theft of protocol/user funds held by a Hinkal component, satisfying the Critical bar (direct theft of funds) since the Emporium contract functions as a shared custody point for in-flight user funds across the whole external-action flow. It is fully repeatable against any token balance Emporium accrues over time.

### Likelihood Explanation
Preconditions are minimal: the attacker needs (1) the Emporium external action registered (already true in production), (2) any valid proof for their own UTXO spend/no-spend flow (self-generated, since only their own note/signature is verified), and (3) the target token(s) to have a nonzero balance on Emporium at call time (a natural byproduct of normal legitimate multi-leg flows). No relayer/owner/admin role, no victim key, and no other privileged capability is required — fully within the stated unprivileged attacker model. Cost is a single transaction plus proof generation for a self-owned/empty flow.

### Recommendation
Do not allow `circomData.erc20TokenAddresses` to diverge from the actual set of tokens `stack.ops` can touch. Either (a) restrict stateless `op.endpoint.call` targets to addresses present in `circomData.erc20TokenAddresses` (and require `erc20TokenAddresses.length > 0` whenever `stack.ops.length > 0` with any stateless op), or (b) have `runAction` snapshot and reconcile Emporium's balance for every token actually touched (e.g., by tracking `balanceOf` deltas for a fixed allowlist, or disallowing raw `call` to arbitrary endpoints entirely in favor of a vetted action registry), so no token balance can change without being accounted for in the balance/slippage equality already enforced in `Hinkal.sol`.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (as the registered external action for a fixed `externalActionId`), and 3 mock ERC20 tokens `T1`, `T2`, `T3`.
2. Seed Emporium with balances of `T1`, `T2`, `T3` (e.g., via legitimate prior deposits/transfers, or direct `mint`/`transfer` to Emporium to simulate residual balances from prior flows).
3. Build a `CircomData` with `erc20TokenAddresses = []`, `externalActionData.externalActionId` = Emporium's id, `externalActionData.externalActionMetadata` = ABI-encoded `EmporiumStack{ signerAddress: address(0), ops: [ {endpoint: T1, invokeWallet:false, value:0, callData: T1.transfer(attacker, T1.balanceOf(emporium))}, {same for T2}, {same for T3} ] }`, and `calldataHash` computed via `CircomDataBuilder.getHashedCalldata`.
4. Generate a valid Groth16 proof for the min-circuit path (`formInputEmporiumMin`) locally using existing circuit artifacts for an empty/no-op UTXO flow.
5. Call `hinkal.transact(a, b, c, dimensions, circomData)` from the attacker EOA.
6. Assert: `T1.balanceOf(emporium) == 0 && T2.balanceOf(emporium) == 0 && T3.balanceOf(emporium) == 0` and `T1.balanceOf(attacker) == preSeededAmount1` (and similarly for T2/T3), while the transaction succeeds without reverting on `BalanceChangeShouldBePositive` or the `Hinkal.sol` balance-diff `require`, proving the equality "assets moved" vs "assets accounted for in `erc20TokenAddresses`" is broken.

### Citations

**File:** contracts/CircomDataBuilder.sol (L20-35)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-124)
```text
        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L312-316)
```text
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
