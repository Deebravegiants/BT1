### Title
Emporium Min-circuit path lets any EOA drain assets held by/approved to the Emporium contract via unconstrained `EmporiumStack.ops` - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `circomData.externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `circomData.erc20TokenAddresses.length == 0`, `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin`, which only binds `message`, `timeStamp`, and `calldataHash` to the Groth16 proof (matching `MainEVMCircuitMin`'s trivial `message <== Poseidon(1)([messageSeed])`). Because `erc20TokenAddresses` is empty, none of `Hinkal.transact`'s balance/slippage checks or `EmporiumUpgradeable.runAction`'s before/after balance accounting cover any asset actually touched by `EmporiumStack.ops`, and if the attacker also sets `stack.signerAddress == address(0)`, `verifyWallet` skips signature verification entirely, leaving `op.endpoint.call{value: op.value}(op.callData)` completely unauthenticated and unaccounted.

### Finding Description
Broken equality: "assets moved by `stack.ops[i].endpoint.call{value: op.value}(op.callData)` executed with `msg.sender == Emporium`" vs. "assets accounted for in `circomData.erc20TokenAddresses`" (which is `[]` in this path). These are supposed to be equal (every asset moved should be tracked/authorized) but they diverge completely.

Path:
1. `Hinkal.transact` calls `hinkalHelper.performHinkalChecks`, which calls `CircomDataBuilder.formInputForCircom` [1](#0-0) . Because `erc20TokenAddresses.length == 0` and `externalActionId == HINKAL_EMPORIUM_ACTION_ID`, `formInputEmporiumMin` is used, producing only 3 public inputs `[emporiumMessage, timeStamp, calldataHash]` [2](#0-1) .
2. The corresponding circuit `MainEVMCircuitMin` only proves knowledge of a Poseidon preimage `messageSeed` for the `message` output — an EOA can trivially pick any `messageSeed`, compute `message = Poseidon(messageSeed)` off-chain, and set `circomData.emporiumMessage = message`. No nullifier, UTXO ownership, or asset-amount is constrained [3](#0-2) .
3. `getHashedCalldata`/`calldataHash` equality check only verifies self-consistency between the attacker's own submitted `circomData` fields and a hash they control themselves — it does not restrict content of `externalActionMetadata` [4](#0-3) .
4. Back in `Hinkal.transact`, the post-action balance/slippage-check loop iterates only over `circomData.erc20TokenAddresses` [5](#0-4) ; since this array is empty, the loop body never executes — no balance-diff, no slippage, no UTXO-amount equality check applies at all for this call.
5. `Hinkal._externalTransact` builds `deltaAmountChanges` sized to `erc20TokenAddresses.length` (i.e., empty) and calls `EmporiumUpgradeable.runAction` [6](#0-5) .
6. Inside `runAction`, `balancesBefore`/`balancesAfter` are also computed only over `circomData.erc20TokenAddresses` (empty), so the subsequent balance-change accounting/`BalanceChangeShouldBePositive` guard never runs for any token actually manipulated by `stack.ops` [7](#0-6) .
7. The attacker sets `stack.signerAddress = address(0)`. `verifyWallet` returns immediately without any ECDSA check when `signerAddress == address(0)` [8](#0-7) , only marking `usedMessages[emporiumMessage] = true` — a value the attacker fully controls.
8. With `invokeWallet = false`, execution falls into "CASE 2: Stateless Interaction": `(success, err) = op.endpoint.call{value: op.value}(op.callData);` executed with `msg.sender == Emporium` [9](#0-8) . The attacker can set `op.endpoint` to any ERC20 token held by Emporium and `op.callData` to `transfer(attacker, balance)`, or set `op.value` to drain Emporium's ETH (Emporium has a `receive() external payable {}` [10](#0-9) ).
9. `onlyAllowedRecipient` only restricts who may call `runAction` (must be the whitelisted Hinkal contract) [11](#0-10) ; it does nothing to constrain `stack.ops` content, since any unprivileged EOA can reach `runAction` through `Hinkal.transact`.

No existing guard (proof, calldataHash check, dimensionsCheck, checkOnchainCreation, balance/slippage loop, `verifyWallet`) constrains or authorizes the actual assets moved by `stack.ops` when `erc20TokenAddresses` is empty and `signerAddress == 0`.

### Impact Explanation
Any funds resting on the Emporium contract (ETH sent via `receive()`, leftover/dust ERC20 balances, or any balance transiently or permanently held there from any user's earlier flow) can be stolen by an unprivileged attacker with a single `Hinkal.transact` call using the Min-circuit path and a crafted `EmporiumStack`. This is direct theft of funds via a call the true owner/prover never authorized, matching the Critical bar ("direct theft of shielded or in-flight user funds ... executing calls or moving assets a wallet owner or prover never authorised"). The attack is repeatable for as long as balance exists on Emporium and each `emporiumMessage` nonce is unique (trivially satisfied since attacker freely chooses `messageSeed`/`emporiumMessage`).

### Likelihood Explanation
Preconditions: Emporium contract must hold some ETH/ERC20 balance at attack time (e.g., leftover from prior legitimate flows, direct ETH transfers via its permissive `receive()`, or dust). Attacker cost is a single valid Groth16 proof for the trivial `MainEVMCircuitMin` (self-satisfiable by any party with no secret knowledge) plus gas. No relayer, admin, or victim cooperation is needed — attacker just constructs `circomData` and an `EmporiumStack` themselves. Feasibility is high given the design gap (empty-array checks + signature bypass at `signerAddress == 0`) and fully repeatable per balance-holding event.

### Recommendation
- Do not allow `EmporiumStack.ops` with `endpoint.call` to be reachable when `signerAddress == address(0)` unless the moved assets are fully tracked; either require `erc20TokenAddresses` to enumerate every token/ETH touched by `stack.ops` (and enforce that in `runAction`'s balance accounting) or disallow the Min-circuit optimization entirely for actions containing arbitrary external calls.
- Require `verifyWallet` to always validate a real signature (never skip on `signerAddress == 0`), or otherwise cryptographically bind `stack.ops` to an authenticated principal.
- Ensure Emporium never carries a residual balance across transactions (sweep fully, or use per-call escrow) so that even if ops are unconstrained, there is nothing exploitable to steal.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (as allowed recipient), register the Min verifier (`VerifierEVMMin0v4`/`mainEVMCircuitMin0v4`) under `buildVerifierId` for `HINKAL_EMPORIUM_ACTION_ID`.
2. Simulate a legitimate prior flow that leaves an ERC20 token `X` balance on the Emporium contract (e.g., a normal Emporium `runAction` where `handleOut` under-collects due to dust, or directly `deal(address(token), emporium, 1000e18)` to model "funds sitting on Emporium contract").
3. As an unrelated EOA (attacker), generate a valid Groth16 proof for `MainEVMCircuitMin` with a freely chosen `messageSeed`, compute `message = Poseidon(messageSeed)` off-chain, set `circomData.emporiumMessage = message`, `circomData.erc20TokenAddresses = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalAddress = emporium`, and encode `externalActionMetadata` as an `EmporiumStack` with `signerAddress = address(0)`, one `op` with `invokeWallet = false`, `endpoint = address(token)`, `callData = abi.encodeCall(token.transfer, (attacker, 1000e18))`, `value = 0`.
4. Call `Hinkal.transact(a, b, c, dimensions, circomData)` from the attacker EOA.
5. Assert: `token.balanceOf(emporium)` before == 1000e18, after == 0; `token.balanceOf(attacker)` before == 0, after == 1000e18. Assert `circomData.erc20TokenAddresses.length == 0` throughout (i.e., no accounting caught the transfer), proving the equality "assets moved by ops" ≠ "assets accounted for in `erc20TokenAddresses`" is broken and directly exploitable.

### Citations

**File:** contracts/CircomDataBuilder.sol (L134-148)
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

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-151)
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
