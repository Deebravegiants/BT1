### Title
Emporium `HINKAL_EMPORIUM_ACTION_ID` with empty `erc20TokenAddresses` allows unbacked, repeatable drain of any Emporium-held funds - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `circomData.erc20TokenAddresses.length == 0`, both `Hinkal.transact()` and `EmporiumUpgradeable.runAction()` skip every balance-conservation check because the check loops are bounded by `erc20TokenAddresses.length`, and `verifyWallet` skips signature verification when `stack.signerAddress == address(0)`. The ZK proof required for this path (`MainEVMCircuitMin`) proves nothing about UTXO ownership - only `message = Poseidon(messageSeed)` - so an unprivileged attacker can trivially self-generate valid proofs and use `EmporiumOperation.endpoint.call` to move out any ETH/ERC20 balance transiently sitting on the Emporium contract, repeating the attack indefinitely with a fresh `emporiumMessage` each time.

### Finding Description
The broken equality is the value-conservation invariant that should hold for every `transact()` call:
`balanceDif == (onChainCreation? 0 : amountChanges[i]) + utxoAmount` for every token touched, checked in `Hinkal.sol` at [1](#0-0) , and the analogous check `balanceChange >= 0` / `handleOut` in `EmporiumUpgradeable.runAction` at [2](#0-1) .

Both checks are `for (i = 0; i < circomData.erc20TokenAddresses.length; i++)` loops. When the attacker sets `erc20TokenAddresses = []` (which is the officially supported "Emporium Min" mode, selected in `CircomDataBuilder.formInputForCircom`: [3](#0-2) ), these loops execute zero times - no balance is ever compared, in either contract.

The proof required for this mode is `MainEVMCircuitMin`, whose only public inputs/outputs are `outTimeStamp`, `calldataHash`, and `message = Poseidon(messageSeed)` [4](#0-3) . It contains no root-hash, nullifier, or amount constraints - it does not prove the attacker owns any shielded UTXO. `performHinkalChecks` only additionally validates `originalSender`/`relay` consistency, `calldataHash` integrity, relay whitelisting (bypassed by setting `relay = address(0)` and calling as `msg.sender == originalSender`, per `relayerIsValid` [5](#0-4) ), `dimensionsCheck` (all zero-length arrays are internally consistent), and `checkOnchainCreation` (vacuous for empty arrays) — see [6](#0-5) . `rootHashExists` still runs in `Hinkal.transact()`, but the attacker can supply any historically valid root (e.g. index 0), which is unrelated to owning funds.

Inside `runAction`, `verifyWallet` only enforces the single-use `usedMessages[emporiumMessage]` guard and, when `stack.signerAddress == address(0)`, returns immediately without any signature check: [7](#0-6) . The attacker picks a fresh `messageSeed`/`emporiumMessage` every call, so this guard never blocks repetition (it only prevents *replaying the same* message, not repeated distinct drains). With `signerAddress == 0`, ops execute as stateless calls: `op.endpoint.call{value: op.value}(op.callData)` [8](#0-7) . The attacker fully controls `endpoint`/`callData` (only `callHinkalWallet`/`doSendToRelay` selectors are blocked). They can target any ERC20 token contract with `transfer(attacker, balanceOf(Emporium))`, or target an arbitrary contract to move out ETH held by Emporium (which has a `receive()` function and thus can accumulate ETH, per [9](#0-8) ).

Because `erc20TokenAddresses = []`, `deltaAmountChanges` is also an empty array (sized to `erc20TokenAddresses.length` in `Hinkal._externalTransact`: [10](#0-9) ), so no UTXO is spent or created to account for the drained value, and the "balance vs. UTXO" equality is never evaluated for the stolen token at all - neither before nor after the call, on either side.

### Impact Explanation
Any ETH/ERC20 balance that transiently sits on the Emporium contract (funds in transit during multi-step swaps, dust/partial leftovers from other users' legitimate `runAction` flows) can be stolen by any unprivileged attacker who is not the owner of those funds. This is a direct theft of in-flight user/protocol funds with no proof-of-ownership requirement and no accounting side effect (no nullifier spent, no commitment created), matching **Critical** severity. It is fully repeatable: the attacker simply picks a new `messageSeed` (hence new `emporiumMessage`) for each call, so `usedMessages` never blocks a second, third, or Nth drain.

### Likelihood Explanation
Preconditions are inherent to normal protocol operation: Emporium acting as an intermediary contract for swaps/deposits will, by design, hold balances during the a call's execution. The attacker's cost is only gas plus generating a trivial `MainEVMCircuitMin` proof (self-computable Poseidon preimage, no dependency on any Merkle tree state or ownership of funds). No special role, whitelisting, or victim cooperation is required - only that the attacker calls `transact()` as `originalSender == msg.sender` with `relay == address(0)`. This makes the attack highly likely and cheap to execute whenever Emporium is holding any residual balance.

### Recommendation
Do not gate the balance-conservation checks in `Hinkal.transact()` and `EmporiumUpgradeable.runAction` solely on `erc20TokenAddresses.length`. For the Emporium-min/stateless path, either: (1) require `erc20TokenAddresses` to enumerate every token the `ops` could possibly touch and enforce the existing balance-diff equality against it, or (2) track and check the full native-ETH and pre-declared token balance of the Emporium contract independent of `erc20TokenAddresses`, ensuring `balanceAfter <= balanceBefore` for every asset not explicitly accounted for by a UTXO output, and require the attacker to actually declare/own the assets being moved rather than allowing `erc20TokenAddresses = []` to bypass conservation entirely. Additionally, when `stack.signerAddress == address(0)`, the stateless op path should not be permitted to call arbitrary `endpoint`s that can move Emporium's own held assets to `msg.sender` without a matching, checked balance delta.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable`, a mock ERC20, and seed the Emporium contract with a balance of that ERC20 (and/or ETH) to simulate "funds in transit" (e.g., via a legitimate `runAction` call that leaves dust, or by directly transferring tokens to the Emporium address to model leftover balance).
2. For `N` iterations, craft a `CircomData` with: `erc20TokenAddresses = []`, `amountChanges = []`, `onChainCreation = []`, `slippageValues = []`, `inputNullifiers = []`, `outCommitments = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalActionMetadata = abi.encode(EmporiumStack({signerAddress: address(0), ops: [EmporiumOperation({endpoint: address(mockERC20), invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, mockERC20.balanceOf(address(emporium))))})], maxFee: 0, deadline: block.timestamp})`, and a fresh `emporiumMessage = Poseidon(messageSeed_i)` for a locally chosen `messageSeed_i`.
3. Generate a valid `MainEVMCircuitMin` proof locally for each `(messageSeed_i, calldataHash, timeStamp)`.
4. Call `hinkal.transact(a, b, c, dimensions, circomData)` from the attacker EOA with `relay = address(0)`, `originalSender = attacker`.
5. Assert: (a) call succeeds each time despite `erc20TokenAddresses = []`; (b) `mockERC20.balanceOf(attacker)` strictly increases on each iteration; (c) `mockERC20.balanceOf(address(emporium))` goes to zero; (d) no nullifier was inserted and no new commitment/UTXO was created for the drained value (`insertNullifiers`/`insertCommitments` receive empty arrays); (e) repeat with a distinct `emporiumMessage` per call to show `usedMessages` never triggers `UsedMessage()` revert, proving unlimited repeatability.

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

**File:** contracts/Hinkal.sol (L244-261)
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

        return
            IExternalActionV2(circomData.externalActionData.externalAddress)
                .runAction(circomData, deltaAmountChanges);
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L102-113)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L369-370)
```text
    receive() external payable {}
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

**File:** contracts/HinkalHelper.sol (L30-35)
```text
    function relayerIsValid(address relay) internal view {
        if (relay != address(0)) {
            require(tx.origin == relay, "Unauthorized relay");
            require(isRelayInList(relay), "Relay is not whitelisted");
        }
    }
```

**File:** contracts/HinkalHelper.sol (L204-236)
```text
    ///@notice make performance checks for transactions
    ///@dev Check if transacaction is valid before making it
    ///@param circomData circom data
    ///@return inputForCircom
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
