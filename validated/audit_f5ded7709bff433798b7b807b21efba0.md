### Title
Emporium ETH drain via unauthenticated `EmporiumOperation` when `signerAddress == address(0)` and `erc20TokenAddresses.length == 0` bypasses all balance checks - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
An unprivileged attacker can call `Hinkal.transact` with `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and an empty `erc20TokenAddresses` array, causing `CircomDataBuilder.formInputForCircom` to select `formInputEmporiumMin`, whose circuit (`MainEVMCircuitMin`) only proves knowledge of a self-chosen `messageSeed` and constrains nothing about the `EmporiumOperation` list. Combined with `EmporiumUpgradeable.verifyWallet` skipping signature verification entirely when `stack.signerAddress == address(0)`, the attacker can craft an arbitrary `EmporiumOperation{endpoint: attackerEOA, invokeWallet:false, value: <Emporium's ETH balance>, callData:""}` that directly drains any ETH sitting in the `Emporium` contract, with none of `Hinkal.transact`'s balance/slippage invariants ever executing because the token array is empty.

### Finding Description
The claimed broken equality is `balanceDif == amountChanges + utxoAmount`, enforced per-token in `Hinkal.transact`'s loop over `circomData.erc20TokenAddresses` [1](#0-0) . When `erc20TokenAddresses.length == 0`, this loop body never executes, so this equality is never checked for any ETH moved during the call — confirmed by tracing `oldBalances`/`newBalances` which are also computed over the same empty array [2](#0-1) .

`dimensionsCheck` allows `dimensions.tokenNumber == 0` (and correspondingly `nullifierAmount == 0`) as a fully valid configuration — it only requires the various arrays' lengths to match `dimensions.tokenNumber`, with no lower bound [3](#0-2) . This causes `CircomDataBuilder.formInputForCircom` to select `formInputEmporiumMin`, whose only public inputs are `emporiumMessage`, `timeStamp`, `calldataHash` [4](#0-3) . The corresponding circuit, `MainEVMCircuitMin`, does nothing but hash a private `messageSeed` the attacker fully controls — no nullifier, ownership, or UTXO constraint exists in this circuit at all [5](#0-4) . `calldataHash` is only checked for self-consistency against attacker-supplied `circomData` via `getHashedCalldata`, which the attacker trivially satisfies since they construct both sides [6](#0-5) .

In `EmporiumUpgradeable.runAction`, `verifyWallet` returns immediately without any signature check once `stack.signerAddress == address(0)`, only marking `emporiumMessage` used for replay protection [7](#0-6) . The subsequent loop then executes `op.endpoint.call{value: op.value}(op.callData)` directly in the "Stateless Interaction" branch for any op with `invokeWallet == false` (or forced there when `signerAddress == address(0)`) [8](#0-7) . `Emporium` can legitimately hold ETH via its own `receive()` function [9](#0-8) . Since `circomData.erc20TokenAddresses` is empty, the post-loop balance-reconciliation in `runAction` (lines 122-159) also iterates zero times, and back in `Hinkal.transact` the balance/slippage-equality checks never run at all for this ETH.

The attacker's exact call: `Hinkal.transact` with `dimensions.tokenNumber = 0`, `circomData.erc20TokenAddresses = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalActionMetadata = abi.encode(EmporiumStack{v,r,s: 0, signerAddress: address(0), ops: [EmporiumOperation{endpoint: attackerEOA, invokeWallet:false, value: <balance>, callData: ""}], maxFee:0, deadline: type(uint256).max})`, and a locally-generated Groth16 proof for `MainEVMCircuitMin` with a self-chosen `messageSeed`.

### Impact Explanation
Direct, unauthorized theft of ETH held by the `Emporium` contract (belonging to the protocol or other in-flight user funds sitting in `Emporium`'s balance) to an attacker-controlled EOA, with zero UTXO ownership, zero nullifier consumption, and zero signature authorization required. This is repeatable for any ETH balance that subsequently accumulates in `Emporium` (each attack requires only a fresh `emporiumMessage` value to avoid `UsedMessage`). This matches the Critical severity category: direct theft of shielded/in-flight funds via an action that was never constrained by the proof or bound to any signer.

### Likelihood Explanation
Precondition: `Emporium` must hold ETH directly (not delegated to a per-user `HinkalWallet`), which is possible since it has a bare `receive()` function and can accumulate ETH from refunds/relay-fee flows/misdirected sends. Given that precondition, the attack has no other barrier: the attacker needs only a self-consistent `calldataHash`, a locally generated proof for the trivial `MainEVMCircuitMin` circuit, and `dimensions.tokenNumber = 0` (a valid combination per `dimensionsCheck`). No relay, admin, or victim cooperation is required, and cost is just gas plus proof generation.

### Recommendation
Do not allow `EmporiumOperation`s with unrestricted `endpoint`/`value` to execute when `stack.signerAddress == address(0)` without a valid signature — signature verification in `verifyWallet` must not be skippable this way, or `signerAddress == address(0)` should be disallowed whenever `stack.ops` contains any operation moving value/ETH out of `Emporium`. Additionally, `Hinkal.transact`'s balance/slippage-equality enforcement should not be entirely skippable via `erc20TokenAddresses.length == 0` for external actions capable of moving ETH; consider requiring at least the native-asset entry in `erc20TokenAddresses` whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID`, or have `formInputEmporiumMin` be usable only for actions provably incapable of moving value out of the protocol.

### Proof of Concept
Foundry fork test:
1. Deploy `Hinkal`, `EmporiumUpgradeable`, register `Emporium` under `HINKAL_EMPORIUM_ACTION_ID`, register a real `MainEVMCircuitMin` verifier under the `buildVerifierId` for `tokenNumber=0, nullifierAmount=0, outputAmount=0, externalActionId=HINKAL_EMPORIUM_ACTION_ID`.
2. Seed `Emporium` with ETH (e.g., send ETH directly to it via its `receive()`), record `emporiumEthBefore`.
3. As attacker EOA, build `CircomData` with `erc20TokenAddresses=[]`, `amountChanges=[]`, `inputNullifiers=[]`, `outCommitments=[]`, `onChainCreation=[]`, `slippageValues=[]`, `externalActionData.externalActionMetadata = abi.encode(EmporiumStack{signerAddress: address(0), ops:[{endpoint: attackerEOA, invokeWallet:false, value: emporiumEthBefore, callData:""}], maxFee:0, deadline: type(uint256).max})`, compute `calldataHash` via `getHashedCalldata` locally, choose `messageSeed`, compute `emporiumMessage = Poseidon(messageSeed)`, generate Groth16 proof `(a,b,c)` for `MainEVMCircuitMin` with public inputs `[timeStamp, calldataHash]` (per `formInputEmporiumMin` ordering) and private input `messageSeed`.
4. Call `Hinkal.transact(a,b,c,dimensions,circomData)` from attacker EOA.
5. Assert: `attackerEOA.balance` increased by exactly `emporiumEthBefore`; `Emporium`'s ETH balance decreased to 0; assert that the loop computing `balanceDif == amountChanges[i] + utxoAmount` in `Hinkal.transact` (lines 97-147) was never entered (e.g., by checking `circomData.erc20TokenAddresses.length == 0` and that no `slippage`/`Balance Diff` revert occurred despite the drain) — demonstrating `VALUE_CONSERVATION` was never enforced for the stolen ETH.

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

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L308-316)
```text
        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;

        if (stack.signerAddress == address(0)) {
            return;
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L369-369)
```text
    receive() external payable {}
```
