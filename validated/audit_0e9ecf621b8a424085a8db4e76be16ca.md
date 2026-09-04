### Title
Unauthenticated invocation of `Emporium.runAction` via the zero-token fast-path bypasses signature check and the `Hinkal.transact` balance equation - ([File: contracts/CircomDataBuilder.sol], [File: circuits/MainEVMCircuitMin.circom], [File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol], [File: contracts/Hinkal.sol])

### Summary
When `circomData.externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `circomData.erc20TokenAddresses.length == 0`, `CircomDataBuilder.formInputForCircom` routes the transaction to `formInputEmporiumMin`, which is verified against `MainEVMCircuitMin` instead of the full `MainEVMCircuit`. That minimal circuit performs **no** EdDSA signature check, no nullifier consumption, and no Merkle-root binding — it only proves that some `messageSeed` chosen by the prover hashes (via a single `Poseidon`) to the `message`/`emporiumMessage` value supplied in calldata. Any unprivileged EOA can pick an arbitrary `messageSeed`, compute the corresponding hash, and produce a trivially valid Groth16 proof with zero secret knowledge of any shielded balance or wallet key. [1](#0-0) [2](#0-1) 

Because `erc20TokenAddresses.length == 0`, the per-token balance-equation/slippage-enforcement loop in `Hinkal.transact` never executes at all (the `for` loop bound is `circomData.erc20TokenAddresses.length`): [3](#0-2) 

`Hinkal._externalTransact` then calls `Emporium.runAction(circomData, deltaAmountChanges)` with an empty `deltaAmountChanges` array: [4](#0-3) 

Inside `runAction`, `verifyWallet` is the only gate on the caller-supplied `EmporiumStack`. If the caller sets `stack.signerAddress == address(0)`, the function returns immediately after just marking `emporiumMessage` used — no EIP-712 signature is ever checked: [5](#0-4) 

The attacker-controlled `ops` array is then executed with the Emporium contract itself as `msg.sender`, using the Emporium contract's own held balance (any ETH from its `receive()` fallback, or dust/fees/leftover token balance), with only a selector blacklist for `callHinkalWallet`/`doSendToRelay`: [6](#0-5) 

### Finding Description
`formInputEmporiumMin` is intended as a "no shielded funds involved" fast path for Emporium meta-transactions, but it removes every authorization primitive that the rest of the protocol relies on:
- No `signedMessageHash`/EdDSA signature (present in `MainEVMCircuit` at `circuits/MainEVMCircuit.circom:33,92-95` but absent from `MainEVMCircuitMin`).
- No nullifier or root binding (no `inNullifiers`, `rootHashHinkal` constraint inside the circuit).
- `emporiumMessage`, the only "authenticated" value, is fully attacker-chosen because it equals `Poseidon(messageSeed)` for an attacker-chosen `messageSeed` — this is not a commitment to any secret, it is a self-consistency tautology.

`performHinkalChecks` in `HinkalHelper.sol` only checks that `calldataHash` is internally consistent with the supplied `circomData` fields (via `getHashedCalldata`) — it does not verify that any of those fields were authorized by a legitimate owner when `erc20TokenAddresses` is empty, since there is no shielded UTXO/signature tying `circomData.externalActionData` (the `EmporiumStack`) to anyone's key. [7](#0-6) 

Combined with `verifyWallet`'s early return for `stack.signerAddress == address(0)`, this means the Emporium contract can be forced to make **any** external call (`op.endpoint.call{value: op.value}(op.callData)`) that the attacker chooses, funded by whatever native ETH/tokens the Emporium contract happens to hold, without any of: a valid EdDSA-signed shielded transaction, a valid EIP-712 wallet signature, or a Hinkal-side balance/slippage check (that check block is skipped entirely because `erc20TokenAddresses.length == 0`).

### Impact Explanation
This breaks the "external action not authorised by prover or signer" invariant and the "value moved by Hinkal or external action not counted in the balance equation" invariant simultaneously:
- Any value the Emporium contract holds (native ETH accepted via its unconditional `receive()`, or ERC20/ETH balances left over from prior legitimate `runAction` executions, relay-fee flows, or race conditions between deposit and spend within multi-step flows) can be swept or misused by an arbitrary unprivileged caller, entirely bypassing Hinkal's balance-equation and slippage protections.
- Because no signature or ZK secret is required, this is not a "malicious relayer" scenario — a fully unprivileged EOA, with no shielded balance and no wallet key, can drive `Emporium.runAction` to make arbitrary external calls as the Emporium contract.

This maps to High severity: theft/misuse of protocol-held funds and execution of calls the protocol/prover never authorized (per the classification rubric).

### Likelihood Explanation
Likelihood is High for triggering the code path (it only requires calling `Hinkal.transact` with `erc20TokenAddresses = []`, `externalActionId = HINKAL_EMPORIUM_ACTION_ID`, a self-generated trivial `MainEVMCircuitMin` proof, and `EmporiumStack.signerAddress = address(0)`). The magnitude of loss depends on how much value the Emporium contract holds at the time of attack, which I could not fully verify from the available files (e.g., whether the deployment guarantees the contract's balance is always zero between transactions). This uncertainty should be resolved by checking actual on-chain/deployed Emporium balances and any invariant tests asserting balance == 0 after every `runAction` call.

### Recommendation
- Require `MainEVMCircuitMin`/the zero-token Emporium path to still bind and verify an authenticating signature (e.g., always require `stack.signerAddress != address(0)` and enforce the EIP-712 check), or otherwise cryptographically tie `emporiumMessage` to a real secret rather than an attacker-chosen `messageSeed`.
- Enforce that `Emporium`'s contract balance is zero (or explicitly accounted for) both before and after every `runAction`, independent of `erc20TokenAddresses.length`, so that no residual funds are ever exposed to the zero-token fast path.
- Consider removing the `signerAddress == address(0)` bypass in `verifyWallet`, or restrict its use to cases where `deltaAmountChanges` is provably non-empty and tied to a verified ZK proof from `MainEVMCircuit` (not `MainEVMCircuitMin`).

### Proof of Concept
1. Attacker (no shielded balance, no wallet key) picks any `messageSeed`, computes `emporiumMessage = Poseidon(messageSeed)`, and generates a valid Groth16 proof for `MainEVMCircuitMin` (trivial — requires no secret).
2. Attacker crafts `circomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `externalActionData = { externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalAddress: <Emporium>, externalActionMetadata: abi.encode(EmporiumStack{ signerAddress: address(0), ops: [{endpoint: <attacker/target>, invokeWallet: false, value: <Emporium's ETH/token balance>, callData: <arbitrary>}], maxFee: 0, deadline: type(uint256).max }) }`, and computes `calldataHash`/`signedMessageHash` to be self-consistent (no real signer needed for the EdDSA check since `MainEVMCircuitMin` never invokes `SignatureVerifier`).
3. Attacker calls `Hinkal.transact(a, b, c, dimensions, circomData)`. `verifyProof` succeeds (trivial proof), `rootHashExists` succeeds for any valid historical root, and the balance-equation loop is skipped because `erc20TokenAddresses.length == 0`.
4. `Hinkal._externalTransact` invokes `Emporium.runAction`, `verifyWallet` returns early (no signature check since `signerAddress == address(0)`), and the attacker's `ops[0]` executes `op.endpoint.call{value: <Emporium balance>}(callData)` as the Emporium contract, moving out any funds the Emporium contract held — with no authorization from any owner and no on-chain balance check.

### Citations

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

**File:** circuits/MainEVMCircuitMin.circom (L1-18)
```text

pragma circom 2.1.6;

include "../../node_modules/circomlib/circuits/poseidon.circom";

template MainEVMCircuitMin() {
  // Public inputs:
  signal input outTimeStamp;
  signal input calldataHash;

  // Private inputs:
  signal input messageSeed;

  // outputs:
  signal output message;

  message <== Poseidon(1)([messageSeed]);
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

**File:** contracts/Hinkal.sol (L234-261)
```text
    function _externalTransact(
        CircomData calldata circomData
    ) internal returns (UTXO[] memory) {
        require(
            externalActionMap[circomData.externalActionData.externalActionId] ==
                circomData.externalActionData.externalAddress &&
                circomData.externalActionData.externalAddress != address(0),
            "Unknown externalAddress"
        );

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

        return
            IExternalActionV2(circomData.externalActionData.externalAddress)
                .runAction(circomData, deltaAmountChanges);
    }
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

**File:** contracts/HinkalHelper.sol (L208-236)
```text
    function performHinkalChecks(
        CircomData calldata circomData,
        Dimensions calldata dimensions,
        address sender
    ) external view returns (uint256[] memory) {
        require(
            (circomData.originalSender == address(0) &&
                circomData.relay != address(0)) ||
                (circomData.originalSender == sender &&
                    circomData.relay == address(0)),
            "invalid value for originalSender"
        );

        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
        relayerIsValid(circomData.relay);
        dimensionsCheck(circomData, dimensions);
        checkOnchainCreation(circomData);

        return
            CircomDataBuilder.formInputForCircom(
                block.chainid,
                hinkalAddress,
                circomData
            );
    }
```
