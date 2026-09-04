### Title
Balance-equation bypass via pre/post transaction hooks excluded from slippage/balance accounting - (File: contracts/Hinkal.sol)

### Summary
`Hinkal.transact()` snapshots ERC20/ETH balances immediately before executing the internal/external action and checks them immediately after, then enforces a strict balance equation (`balanceDif == amountChanges + utxoAmount`, with a slippage floor). However, the `preHookContract.preTransact()` call happens *before* the `oldBalances` snapshot, and the `postHookContract.afterTransact()` call happens *after* the balance-equation check has already passed. Both hook addresses and their arbitrary metadata (`hookData.preHookMetadata` / `postHookMetadata`) are fully attacker-controlled fields of `CircomData`, bound only by `calldataHash`/the ZK proof — the proof only attests that the *prover* chose these values, it does not constrain what they cause to happen on-chain.

### Finding Description
In [1](#0-0)  the sequence is:
1. `performSideEffects` (no-op).
2. `preHookContract.preTransact(circomData)` is invoked **before** `oldBalances` is captured.
3. `_internalTransact`/`_externalTransact` executes the accounted-for token movement.
4. `newBalances` is captured and the balance equation in [2](#0-1)  is enforced.
5. Only *after* that equation succeeds does `postHookContract.afterTransact(circomData)` run, per [3](#0-2) .

Both `hookData.preHookContract`/`postHookContract` and their metadata are plain fields of `CircomData` chosen by the calling user/prover, and are only bound into `calldataHash` (`getHashedCalldata2`) as seen in [4](#0-3) . Being bound in `calldataHash` only proves the value was *fixed at proof time* — the same “strategyProof vs global proof” class of gap from the external report: an equality (`balanceDif == accounted change`) is enforced only over a window in the call graph that both hooks fall outside of. Since `Hinkal.sol` calls these hook contracts with `msg.sender == address(Hinkal)`, and `Hinkal` holds the entire pooled/shielded balance of all users, any contract logic reachable through `preTransact`/`afterTransact` that causes ERC20/ETH to leave `Hinkal` (directly, or by using a stale `approve` previously granted by `Hinkal` to that same hook address as part of a legitimate external-action integration) moves shielded-pool funds that are never subjected to the balance/slippage equality check that is supposed to bound every state-changing `transact()` call.

This breaks the same invariant class flagged in the external report: a value-moving path exists that bypasses the equality the protocol relies on to guarantee `balanceDif == accounted change`, because the accounting window (`oldBalances`→`newBalances`) does not span the full set of external calls Hinkal makes on the user’s behalf.

### Impact Explanation
If a hook contract that already holds standing approval/allowance from `Hinkal` (e.g. a previously-integrated DeFi adapter reachable via the same hook interface) is specified as `postHookContract`, any transfer it triggers after the balance check happens with zero on-chain enforcement — this is unaccounted movement of the shared/shielded pool's assets, i.e., theft or freezing of other users’ funds, which matches the Critical/High impact bar (“value moved by Hinkal … but not counted in the balance equation”).

### Likelihood Explanation
Exploitability depends entirely on whether any hook contract accepted by the protocol (or reachable via `preTransact`/`afterTransact`) ever holds a token allowance from `Hinkal` or otherwise can move tokens out of `Hinkal` when called with `msg.sender == Hinkal`. I could not verify within the indexed contracts whether such a hook contract exists or is deployed/whitelisted — `hookData.preHookContract`/`postHookContract` are not checked against any allow-list in `Hinkal.sol` or `HinkalHelper.sol`, and no hook implementation was found in the indexed `contracts/**` (the interfaces `IPreTransactHook`/`ITransactHook` in `contracts/types/ITransactHook.sol` have no in-scope concrete implementers I could locate). This is a real structural gap in the accounting window, but I cannot confirm a concrete exploitable hook implementation exists in-scope, so likelihood cannot be fully established without further investigation (e.g. a Devin session with full repo access to search for any hook contracts elsewhere, or the wallet/emporium action files not shown in the index).

### Recommendation
Either (a) require `preTransact` to run before the balance snapshot only if it cannot move `erc20TokenAddresses` balances (enforce via a return value/whitelist), or (b) move the `oldBalances` snapshot before `preTransact` and the `newBalances`/equation check after `afterTransact`, so the full external-call surface of a `transact()` invocation is captured by the balance equation. Additionally, hook contract addresses should be restricted to a governance-controlled allow-list rather than being freely user-supplied `CircomData` fields.

### Proof of Concept
Conceptual (not verifiable against a concrete hook implementation with current index access):
1. Attacker crafts a valid ZK proof for a `transact()` call with `circomData.hookData.postHookContract = X`, where `X` is some contract that, given `circomData` and knowing `msg.sender == Hinkal`, can trigger `IERC20(token).transferFrom(hinkalAddress, attacker, amount)` using a pre-existing allowance from `Hinkal` to `X` (established via a legitimate prior integration flow), or can otherwise cause `Hinkal` to lose ERC20/ETH.
2. Balance snapshot (`oldBalances`) and `newBalances` are taken strictly around `_internalTransact`/`_externalTransact`, per [5](#0-4) .
3. The balance equation passes (attacker's declared `amountChanges`/`utxoAmount` for their own legitimate leg of the transaction is satisfied).
4. `afterTransact` fires post-check per [3](#0-2) , draining `amount` from `Hinkal` with no equality check ever inspecting this movement.

I was unable to confirm the existence of a concrete `X` implementation with such a capability within the indexed files; this should be verified against the full repository (all `external-actions/**` and any wallet/hook implementer contracts) before treating this as confirmed rather than a structural gap.

### Citations

**File:** contracts/Hinkal.sol (L66-90)
```text
        hinkalHelper.performSideEffects(circomData);

        {
            if (circomData.hookData.preHookContract != address(0)) {
                IPreTransactHook transactHook = IPreTransactHook(
                    circomData.hookData.preHookContract
                );
                transactHook.preTransact(circomData);
            }

            UTXO[] memory utxoSet;

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

**File:** contracts/Hinkal.sol (L96-147)
```text
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
            }
```

**File:** contracts/Hinkal.sol (L149-154)
```text
            if (circomData.hookData.postHookContract != address(0)) {
                ITransactHook transactHook = ITransactHook(
                    circomData.hookData.postHookContract
                );
                transactHook.afterTransact(circomData);
            }
```

**File:** contracts/CircomDataBuilder.sol (L37-54)
```text
    function getHashedCalldata2(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.hookData,
                        circomData.encryptedOutputs,
                        circomData.onChainEncryptedOutput,
                        circomData.feeStructure,
                        circomData.onChainCreation,
                        circomData.originalSender,
                        circomData.extraData
                    )
                )
            );
    }
```
