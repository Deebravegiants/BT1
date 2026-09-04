### Title
Emporium "min-path" (`erc20TokenAddresses.length == 0`) bypasses both the on-chain balance equation and the wallet signature check, allowing unauthorized calls/value transfers from the Emporium contract - (File: `contracts/Hinkal.sol`, `contracts/CircomDataBuilder.sol`, `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
When a `transact()` call targets the Emporium external action with `circomData.erc20TokenAddresses.length == 0`, `CircomDataBuilder.formInputForCircom()` routes to `formInputEmporiumMin()`, which feeds only 3 public signals (`emporiumMessage`, `timeStamp`, `calldataHash`) to the verifier [1](#0-0) . Because `erc20TokenAddresses` is empty, the balance-equation loop in `Hinkal.transact()` that normally enforces "change in balance == declared amountChanges + minted UTXO amount" never executes (the `for` loop bound is `circomData.erc20TokenAddresses.length`) [2](#0-1) . Simultaneously, `EmporiumUpgradeable.verifyWallet()` skips ECDSA signature verification entirely whenever `stack.signerAddress == address(0)` [3](#0-2) . With both guards absent, `runAction()` still executes every operation in `stack.ops`, including arbitrary `op.endpoint.call{value: op.value}(op.callData)` from the Emporium contract itself [4](#0-3) .

### Finding Description
The protocol relies on two independent guarantees to make Emporium operations safe:
1. **The balance equation in `Hinkal.transact()`** — ties any value moved during `_externalTransact()` back to the declared `amountChanges`/minted UTXOs for every token in `circomData.erc20TokenAddresses` [5](#0-4) .
2. **The EIP-712 wallet signature in `verifyWallet()`** — ties the exact set of `ops` (`endpoint`, `invokeWallet`, `value`, `callData`) to a signature from `stack.signerAddress` [6](#0-5) .

Both of these are conditioned on non-empty state: guarantee (1) is a `for` loop over `circomData.erc20TokenAddresses`, which is empty by construction on the "min" path used for the Emporium action (this is exactly the condition selecting `formInputEmporiumMin` in `formInputForCircom()`) [7](#0-6) ; guarantee (2) is explicitly skipped when `stack.signerAddress == address(0)` — a caller-controlled field decoded straight out of `circomData.externalActionData.externalActionMetadata` [8](#0-7) .

`formInputEmporiumMin` only feeds `emporiumMessage`, `timeStamp`, and `calldataHash` into the ZK verifier — it omits `rootHashHinkal`, `signedMessageHash` (i.e. the EdDSA-signature-derived public commitment tying the proof to a specific spending key), and the stealth-address fields [9](#0-8) . Since `dimensionsCheck()` only requires internal-array-length consistency (all zero-length arrays trivially satisfy it) and does not require ownership proof of any UTXO when `tokenNumber == 0` [10](#0-9) , this "min" verification path carries essentially no cryptographic authorization tied to a user's private key for this specific action — nothing analogous to the ZEVM-log gap in the source report, where a state-transition side effect (moving/burning value) is triggered by a code path whose authorization channel (log processing) is bypassed.

As a result, any caller who can produce a valid Groth16 proof for the trivial "min" public-input set (a set with no meaningful UTXO-spend constraint) can invoke `Hinkal.transact()` with:
- `circomData.externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID`
- `circomData.erc20TokenAddresses.length == 0` (skips the balance equation entirely)
- `externalActionMetadata` decoding to an `EmporiumStack` with `signerAddress == address(0)` (skips the ECDSA signature check entirely)
- an `ops` array containing arbitrary `(endpoint, invokeWallet=false, value, callData)` entries

`EmporiumUpgradeable.runAction()` will then execute every one of these calls from the Emporium contract's own context, moving `op.value` ETH and issuing arbitrary `callData` to arbitrary `endpoint` addresses, with no equality anywhere in the system constraining what value/state change is "owed" back to any UTXO or signer.

### Impact Explanation
This breaks the "assets moved must be authorized by the prover/signer and backed by the declared balance equation" invariant. Any ETH or approved-token balance sitting in the Emporium contract (fees collected, unswept relay balances, or funds temporarily routed through Emporium during composed operations) can be moved to attacker-chosen destinations via attacker-chosen `callData`, without any signature from a legitimate signer and without triggering the balance-diff check that normally guards `_externalTransact()`. This is unauthorized asset movement / execution of calls a wallet owner or prover never authorized, which the rules classify as High impact (temporary/permanent freezing or theft of protocol/relay funds, or unauthorized call execution).

### Likelihood Explanation
Exploitation requires only: (a) the attacker be able to generate a valid proof for the trivial "min" circuit's public-input set — plausible given the omitted signature/root-hash constraints on that path — and (b) craft `externalActionMetadata` with `signerAddress = address(0)` and arbitrary `ops`. No admin, relayer, or third-party key is needed; only knowledge of the (unprivileged) proving system and the ability to call `Hinkal.transact()` directly, which any EOA can do. Whether this is exploitable in full depends on the actual "min" Circom template's constraints not encoding an implicit ownership check I could not inspect directly (it was not present in the files I could retrieve) — this is the one point of uncertainty in this analysis.

### Recommendation
- Always run the balance-equation check in `Hinkal.transact()` regardless of `circomData.erc20TokenAddresses.length`, or explicitly forbid `erc20TokenAddresses.length == 0` for external actions that can move value/execute calls.
- Require a signer/signature (or otherwise cryptographically bind `stack.ops`) even when `signerAddress == address(0)`; do not allow an unauthenticated `ops` execution path.
- Ensure the "min" circuit used for `formInputEmporiumMin` still encodes a genuine ownership/authorization constraint (e.g., a valid EdDSA signature over `signedMessageHash`) rather than omitting it because `tokenCount == 0`.

### Proof of Concept
Conceptual call sequence (proof generation for the "min" circuit not independently verified against the actual `.circom` source, which was not retrievable):
1. Attacker crafts `circomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `inputNullifiers = []`, `outCommitments = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalActionMetadata = abi.encode(EmporiumStack({signerAddress: address(0), ops: [EmporiumOperation({endpoint: attackerContract, invokeWallet: false, value: <emporiumBalance>, callData: ""})], maxFee: 0, deadline: type(uint256).max}))`.
2. Attacker computes `calldataHash` via `getHashedCalldata` locally to match the on-chain check in `performHinkalChecks` [11](#0-10) .
3. Attacker generates a Groth16 proof `(a, b, c)` for the "min" public inputs `[emporiumMessage, timeStamp, calldataHash]`.
4. Attacker calls `Hinkal.transact(a, b, c, dimensions, circomData)` — `verifyProof` succeeds, `rootHashExists` succeeds (any valid root works since no nullifiers are spent), the balance-equation loop is skipped (0 iterations) [2](#0-1) , and `_externalTransact()` invokes `EmporiumUpgradeable.runAction()`, which skips the signature check (`signerAddress == address(0)`) and executes `op.endpoint.call{value: op.value}(op.callData)`, draining ETH held by the Emporium contract to `attackerContract`.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-90)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L318-340)
```text
        bytes32 hashedMessage = _hashTypedDataV4(
            keccak256(
                abi.encode(
                    EMPORIUM_SIGNATURE_TYPEHASH,
                    circomData.emporiumMessage,
                    _hashEmporiumOps(stack.ops),
                    stack.maxFee,
                    stack.deadline
                )
            )
        );

        (address recoveredAddress, ECDSA.RecoverError err) = ECDSA.tryRecover(
            hashedMessage,
            stack.v,
            stack.r,
            stack.s
        );
        bool verified = err == ECDSA.RecoverError.NoError &&
            recoveredAddress == stack.signerAddress;
        if (!verified) {
            revert InvalidSignature();
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
