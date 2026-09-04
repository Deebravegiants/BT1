### Title
Unrestricted `preHookContract` executes before `oldBalances` snapshot, allowing hook-controlled fund movement to bypass the balance equation - (File: `contracts/Hinkal.sol`)

### Summary
`Hinkal.transact()` allows the caller to specify an arbitrary `circomData.hookData.preHookContract`/`postHookContract` with no whitelist/registry check comparable to `externalActionMap` used for external actions. [1](#0-0)  Unlike the ITS-hub bug (untracked balance created off the balance-tracking equality via an unvetted deployment path), here the `preTransact` hook is invoked *before* the `oldBalances` snapshot used in the balance-conservation check, and `afterTransact` is invoked *after* the balance check but *before* nullifier/commitment insertion, placing both hooks' fund effects outside the equality that is supposed to reconcile on-chain balance changes with `amountChanges`/UTXO amounts.

### Finding Description
In `transact()`:
```
if (preHookContract != 0) { preTransact(circomData); }
oldBalances = getBalancesForArray(...);
... _internalTransact/_externalTransact ...
newBalances = getBalancesForArray(...);
require(balanceDif == amountChanges[i] + utxoAmount, ...);
if (postHookContract != 0) { afterTransact(circomData); }
insertNullifiers(...); insertCommitments(...);
``` [2](#0-1) 

`preHookContract` executes before `oldBalances` is captured, so any balance change it performs (e.g., calling `transferERC20TokenFromOrCheckETH` style logic, or simply being a contract that pulls tokens out of `Hinkal` via an approval it was granted in a prior transaction) is invisible to the subsequent `balanceDif` equality — it is baked into the "before" state. `afterTransact` executes after the equality is enforced but before nullifiers/commitments are recorded, so any balance change it makes also falls outside the checked equality window entirely.

Both `preHookContract` and `postHookContract` are fields of `CircomData` supplied directly by the caller of `transact()`, and are only checked for internal self-consistency via `calldataHash`/`signedMessageHash` (i.e., that the value the prover signed matches what's executed) — there is no on-chain registry restricting which contracts may be designated as hooks, unlike `externalActionMap` which is admin-gated via `registerExternalAction`. [3](#0-2)  The `CircomData.hookData` fields are only included in the `calldataHash` integrity check, not validated against any allowlist. [4](#0-3) 

### Impact Explanation
If a hook contract is registered/reachable at an address the attacker controls (or if any protocol-approved hook contract can be tricked into transferring out contract balance), a caller could construct a `transact()` call whose `preTransact` hook moves ERC20/ETH out of `Hinkal` before the balance snapshot, or whose `afterTransact` hook does so after the check but before state finalization — either path allows funds to leave the pool without being reflected in the enforced `balanceDif == amountChanges + utxoAmount` equality. This breaks the equality the analog targets: "value moved by Hinkal or an external action but not counted in the balance equation." This could permit theft of protocol/pool funds not backed by a corresponding decrease in tracked UTXO value.

### Likelihood Explanation
Exploitability is gated by whether an attacker can actually get an arbitrary/malicious contract accepted as `preHookContract`/`postHookContract` and whether that contract has any means to move `Hinkal`'s balance (e.g., pre-existing approvals, reentrant calls, or acting on `msg.sender`/`address(this)` balances). I could not confirm from the available files whether hook contracts are restricted elsewhere (e.g., via a registry in a file not indexed) or whether `preTransact`/`afterTransact` implementations in this repo ever move funds — I only found the two-line interface `ITransactHook.sol` with no first-party implementation in the indexed files. [5](#0-4)  Because of index size limits, some files (potential hook implementations or an admin-gated hook registry) may not be available to me — I recommend confirming with a full repository checkout (e.g., a Devin session) whether `hookData.preHookContract`/`postHookContract` are constrained anywhere else in the codebase before treating this as confirmed exploitable.

### Recommendation
Snapshot `oldBalances` before invoking `preTransact`, and move the `balanceDif` check to occur strictly after both `preTransact` and `afterTransact` have run (or disallow `afterTransact` from altering token balances, and require any hook contract to be validated against an admin-controlled registry analogous to `externalActionMap`).

### Proof of Concept
Given the incomplete visibility into hook contract implementations/registries in the indexed subset of the repo, I cannot construct a concrete, fully-verified exploit transaction here. The mechanism (ordering of hook calls relative to the balance snapshot/check) is demonstrated directly in `contracts/Hinkal.sol:68-146` cited above; a full PoC requires inspecting/deploying a hook contract implementing `IPreTransactHook`/`ITransactHook` and confirming it is invocable without additional access control, which should be validated with full repository access.

### Citations

**File:** contracts/Hinkal.sol (L22-28)
```text
    function registerExternalAction(
        uint256 externalActionId,
        address externalActionAddress
    ) public onlyRole(DEFAULT_ADMIN_ROLE) {
        externalActionMap[externalActionId] = externalActionAddress;
        emit ExternalActionRegistered(externalActionAddress);
    }
```

**File:** contracts/Hinkal.sol (L68-146)
```text
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

**File:** contracts/types/ITransactHook.sol (L1-12)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.6;

import {CircomData} from "./CircomData.sol";

interface IPreTransactHook {
    function preTransact(CircomData calldata circomData) external;
}

interface ITransactHook {
    function afterTransact(CircomData calldata circomData) external;
}
```
