### Title
Emporium "Min" path lets any EOA drain the Emporium contract's real ETH/ERC20 balance without a meaningful proof or signature - ([File: contracts/CircomDataBuilder.sol], [File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol], [File: circuits/MainEVMCircuitMin.circom])

### Summary
When `circomData.externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `circomData.erc20TokenAddresses.length == 0`, `Hinkal.transact` and `EmporiumUpgradeable.runAction` both skip their balance-conservation checks entirely (their loops are bounded by `erc20TokenAddresses.length`), while the ZK proof required for this path (`MainEVMCircuitMin`) proves nothing except "I know a `messageSeed` whose Poseidon hash equals `emporiumMessage`" — a value the caller freely chooses. Combined with `signerAddress == address(0)` skipping the EIP-712 signature check in `verifyWallet`, an unprivileged EOA can submit a trivially-constructed "proof" and an arbitrary stateless `EmporiumOperation` that calls `op.endpoint.call{value: op.value}(op.callData)`, moving real ETH/ERC20 out of the Emporium contract with no balance equation, no signature, and no real proof-of-authorization enforcing it.

### Finding Description
`CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin` whenever the action is the Emporium action and `erc20TokenAddresses.length == 0`: [1](#0-0) 

That path's public input vector is only `[emporiumMessage, timeStamp, calldataHash]`, and the matching circuit `MainEVMCircuitMin` computes `message <== Poseidon(messageSeed)` with no signature, spending-key, nullifier, or root-hash verification at all: [2](#0-1) 

Since `messageSeed` is chosen by the caller and `Poseidon` is public/forward-computable, any caller can pick `messageSeed`, compute `message = Poseidon(messageSeed)`, set `circomData.emporiumMessage = message`, and produce a *valid* Groth16 proof for this circuit without needing any secret tied to a real Hinkal identity or UTXO. This proof carries no authorization weight.

In `Hinkal.transact`, the post-action balance/UTXO-conservation loop is bounded by `circomData.erc20TokenAddresses.length`, so with `erc20TokenAddresses = []` this loop (which enforces `balanceDif == amountChanges + utxoAmount`) never executes: [3](#0-2) 

`dimensionsCheck` forces `amountChanges`, `inputNullifiers`, `outCommitments`, `onChainCreation`, `slippageValues` to also be zero-length when `tokenNumber == 0`, so there is nothing left to constrain UTXO spends — consistent with "no shielded funds move here."

Inside `EmporiumUpgradeable.runAction`, the same emptiness propagates: `balancesBefore`/`balancesAfter` are computed over the empty `erc20TokenAddresses` array, and the loop that would `revert BalanceChangeShouldBePositive()` on a negative balance change is also bounded by that same empty array, so it never runs: [4](#0-3) 

`verifyWallet` only enforces the EIP-712 signature when `stack.signerAddress != address(0)`; for the stateless case (`signerAddress == address(0)`) it simply marks the message as used and returns — no cryptographic check ties the operation to any user identity: [5](#0-4) 

The stateless operation branch then performs a raw low-level call carrying real value from the Emporium contract itself: [6](#0-5) 

Putting this together: the equality that should hold — "every unit of value the Emporium contract sends out via an `EmporiumOperation` is backed by a proof of a real UTXO/shielded-balance decrease counted in `erc20TokenAddresses`/`amountChanges`" — is broken. With `erc20TokenAddresses = []`, that counting mechanism is entirely absent on both the `Hinkal.sol` side and the `EmporiumUpgradeable.sol` side, yet the `ops` array (which is not part of the calldataHash/signedMessageHash coverage for this Min-path, and whose only "proof" is the self-computable Poseidon preimage) can still direct the Emporium contract to pay out arbitrary `op.value` ETH or invoke arbitrary ERC20 transfers of tokens the Emporium contract holds.

### Impact Explanation
This is theft of protocol/relay-held funds: any pooled ETH or ERC20 balance sitting in the Emporium contract (accumulated from legitimate prior deposits/relay fee flows) can be extracted by an unprivileged EOA who supplies a self-manufactured "proof" requiring no secret knowledge and no signature, directing arbitrary `call{value: ...}` operations from the Emporium contract to attacker-controlled addresses. This satisfies "Critical - direct theft of shielded or in-flight user funds ... proof or nullifier verification bypass," since the very proof gate meant to authorize the Emporium action is cryptographically meaningless in this branch.

### Likelihood Explanation
High. The path is directly reachable by any EOA calling `Hinkal.transact` with `dimensions.tokenNumber == 0`, `externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID`, and `stack.signerAddress == address(0)`. Constructing the Min-circuit proof requires no secret — only forward Poseidon evaluation, which any user can compute off-chain with the same tooling used to generate legitimate proofs.

### Recommendation
- Do not allow the "Min" emporium path to authorize any operation that moves value out of the Emporium contract (`op.value > 0` or arbitrary `callData`) when `signerAddress == address(0)` and there is no real balance-conservation check.
- Bind `MainEVMCircuitMin`'s `message` output to an actual authorization secret (e.g., require it to be derived from a spending key / UTXO nullifier proof), not a bare Poseidon preimage the caller freely selects.
- Ensure `EmporiumUpgradeable.runAction`'s balance-change enforcement (and `Hinkal.transact`'s balance-diff loop) cannot be bypassed simply by supplying zero-length `erc20TokenAddresses`; explicitly reject/ignore stateless value-moving `ops` when there is no accompanying, circuit-verified balance decrease.

### Proof of Concept
1. Attacker (any EOA, no relation to Hinkal) picks any `messageSeed`, computes `message = Poseidon(messageSeed)`, and sets `circomData.emporiumMessage = message`.
2. Attacker builds a valid Groth16 proof for `MainEVMCircuitMin` using only `messageSeed`, `outTimeStamp`, and `calldataHash` — no signature, spending key, or nullifier required.
3. Attacker sets `circomData.erc20TokenAddresses = []`, `circomData.externalActionData = {externalAddress: EmporiumUpgradeable address, externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalActionMetadata: abi.encode(EmporiumStack{signerAddress: address(0), ops: [{endpoint: attacker, invokeWallet: false, value: <EmporiumBalance>, callData: ""}], maxFee:0, deadline: 0})}`.
4. Attacker calls `Hinkal.transact(a,b,c,dimensions={tokenNumber:0,...},circomData)`.
5. `Hinkal.transact`'s balance-diff loop (bounded by `erc20TokenAddresses.length == 0`) never executes; `_externalTransact` calls `EmporiumUpgradeable.runAction` with empty `deltaAmountChanges`.
6. `verifyWallet` returns early (signerAddress is zero); the `ops` loop executes `op.endpoint.call{value: op.value}("")`, sending the Emporium contract's ETH balance to the attacker; `BalanceChangeShouldBePositive` never triggers because its loop is also bounded by the empty `erc20TokenAddresses` array.

### Citations

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

**File:** contracts/Hinkal.sol (L92-147)
```text
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
            }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-150)
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
