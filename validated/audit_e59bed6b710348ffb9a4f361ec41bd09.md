### Title
Emporium `runAction` lets an unprivileged prover drain the contract's native-ETH balance via unaccounted `op.value` calls - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction` executes arbitrary `EmporiumOperation`s decoded from `circomData.externalActionData.externalActionMetadata`. When `stack.signerAddress == address(0)` (or `op.invokeWallet == false`), `verifyWallet` skips signature verification entirely [1](#0-0)  and the operation is executed directly from Emporium's own context: `op.endpoint.call{value: op.value}(op.callData)` [2](#0-1) . The post-call accounting loop only inspects balances for `circomData.erc20TokenAddresses` [3](#0-2) [4](#0-3) , an array fully chosen by the attacker submitting the transaction. If the attacker simply omits `address(0)` from `erc20TokenAddresses`, any native ETH sent out via `op.value` is never checked against `balancesBefore`/`balancesAfter`, so it is invisible to the balance equation.

### Finding Description
`EmporiumUpgradeable` is a shared, multi-user external-action contract: it holds ETH belonging to any user whose shielded UTXOs reference `address(0)` and who is mid-transaction routed through Emporium (funds are pushed in by `Hinkal._externalTransact` via `transferERC20TokenOrETH` before `runAction` is invoked) [5](#0-4) , plus it also has a `receive()` fallback that lets ETH accumulate on it from prior operations [6](#0-5) .

`runAction` decodes an `EmporiumStack` entirely from attacker-supplied `externalActionMetadata` [7](#0-6) . For "stateless" operations (`op.invokeWallet == false`, or any op when `stack.signerAddress == address(0)`), Emporium performs the call itself using its own ETH balance:
```solidity
(success, err) = op.endpoint.call{value: op.value}(op.callData);
``` [2](#0-1) 

When `stack.signerAddress == address(0)`, `verifyWallet` only marks the message used and returns — no EIP-712 signature or wallet ownership is checked at all [8](#0-7) . This means the `ops` array (including `op.value`) is entirely attacker-controlled with no authorization tying it to a specific wallet or to the funds the attacker actually owns.

The only guardrail is the post-loop balance-equality check, but it iterates solely over `circomData.erc20TokenAddresses` — a list the attacker also fully controls as part of the same `CircomData` struct used to build the ZK public inputs [9](#0-8) . If the attacker crafts `circomData` with `erc20TokenAddresses` containing only, e.g., an ERC-20 token (or an empty/irrelevant set) while still embedding an `EmporiumOperation` with a non-zero `op.value` pointing ETH at an attacker-controlled `endpoint`, that native-ETH movement is never captured in `balancesBefore`/`balancesAfter` for any tracked index, so the equality `balanceChange == -deltaAmountChange` is never evaluated for ETH at all. `Hinkal.transact()`'s own top-level balance-diff loop has the identical limitation — it only loops over `circomData.erc20TokenAddresses` too [10](#0-9) . `circomData.calldataHash` guards against a relayer tampering with the attacker's own submitted calldata, but does not constrain what the attacker themselves is allowed to put in that calldata, and no signal in the circuit's public-input vector binds `op.value`/`op.endpoint` to actual owned UTXO amounts for the ETH token type.

Net effect: the value withdrawn via `op.value` is a field acted upon by an external action (Emporium) but is completely excluded from the balance-equation checks in both `Hinkal.transact()` and `EmporiumUpgradeable.runAction()`, because the attacker controls which token indices are checked.

### Impact Explanation
This allows an unprivileged user (any address able to submit a self-crafted, self-signed `transact()` proof for their own trivial UTXOs) to drain Emporium's actual ETH balance — which is shared custody for other users' shielded ETH deposits mid-flow through the Emporium external action, plus any residual ETH left on the contract — to an attacker-chosen address, without that outflow ever appearing in the balance-diff equality checks. This is direct theft of shielded/in-flight user funds held by the contract, matching the Critical impact category ("direct theft of shielded or in-flight user funds").

### Likelihood Explanation
Likelihood is high for any attacker who can generate a valid proof for their own inputs (a fully permissionless operation in this protocol) and who chooses `Emporium` as `externalActionData.externalAddress` with `signerAddress = address(0)`. No relayer, admin, or third-party signature is required to reach the vulnerable code path — `verifyWallet` explicitly special-cases `signerAddress == address(0)` to skip verification. The only prerequisite is that Emporium currently holds spendable ETH (from in-flight user transactions or dust accumulated via `receive()`), which is a normal operating condition for this shared contract.

### Recommendation
- Reject or fee-account for `op.value > 0` calls when `stack.signerAddress == address(0)` (stateless path), since there is no wallet-owner or signer authorization backing that ETH movement.
- Include the native-ETH token (`address(0)`) in the balance-equality check unconditionally (not only when present in `circomData.erc20TokenAddresses`), so any ETH balance decrease on Emporium during `runAction` is always reconciled against `deltaAmountChanges`/UTXO outputs.
- Bind `op.value` for stateless operations to a value explicitly derived from `deltaAmountChanges`/UTXO amounts that the circuit can attest to, rather than an arbitrary attacker-chosen field in `externalActionMetadata`.

### Proof of Concept
1. Attacker ensures Emporium (`EmporiumUpgradeable`) holds ETH (e.g., ETH left mid-flight from a legitimate concurrent user transaction, or dust sent via `receive()`).
2. Attacker builds a valid ZK proof for their own arbitrary CircomData where:
   - `circomData.externalActionData.externalAddress` = Emporium, `externalActionId` = Emporium's registered id.
   - `circomData.erc20TokenAddresses` = `[someERC20Token]` (deliberately excludes `address(0)`).
   - `externalActionMetadata` decodes to an `EmporiumStack` with `signerAddress = address(0)` and one `EmporiumOperation{ endpoint: attackerAddress, invokeWallet: false, value: X, callData: "" }`.
3. Attacker calls `Hinkal.transact(...)` with this proof/circomData. `verifyWallet` skips signature checks (line 314-316), the loop executes `attackerAddress.call{value: X}("")`, transferring `X` wei of Emporium's ETH to the attacker [11](#0-10) .
4. Both `EmporiumUpgradeable.runAction`'s balance loop and `Hinkal.transact`'s balance-diff loop only inspect `circomData.erc20TokenAddresses` (the ERC-20 token, not ETH), so the stolen ETH is never checked against any equality and the transaction succeeds.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-83)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external override onlyAllowedRecipient returns (UTXO[] memory) {
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-145)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L369-369)
```text
    receive() external payable {}
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
