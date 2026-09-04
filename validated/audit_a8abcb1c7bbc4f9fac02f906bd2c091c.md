### Title
Emporium stack signature never binds to `Dimensions`/`erc20TokenAddresses`, letting a signed token-moving `EmporiumStack` be replayed through the unconstrained Min-circuit path - ([File: contracts/types/ITransactHook.sol] / [contracts/CircomDataBuilder.sol] / [contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
The Min circuit (`formInputEmporiumMin`) only publishes 3 signals and its template `MainEVMCircuitMin` never uses `outTimeStamp`/`calldataHash` in any constraint, so an attacker can produce a valid proof for *any* `emporiumMessage`/`calldataHash`/`timeStamp` combination for free. Because `EmporiumUpgradeable.verifyWallet`'s EIP-712 signature only covers `(emporiumMessage, opsHash, maxFee, deadline)` and never covers `Dimensions`, `erc20TokenAddresses`, or `calldataHash`, a legitimately signed `EmporiumStack` intended for a real token-moving transaction (`erc20TokenAddresses.length > 0`) can be resubmitted wrapped in a new `circomData` with `erc20TokenAddresses = []`, forcing selection of the Min verifier via `buildVerifierId`, and still executes the exact same `stack.ops` (including `callHinkalWallet`/`doSendToRelay`) with zero balance/UTXO accounting.

### Finding Description
The broken equality: (verifier/circuit dimension the wallet owner's EIP-712 signature was scoped to authorize) != (verifier dimension `Hinkal.transact` actually accepts the proof under).

- `verifyWallet` computes the signed hash from only `circomData.emporiumMessage`, `_hashEmporiumOps(stack.ops)`, `stack.maxFee`, `stack.deadline` [1](#0-0) . `Dimensions`, `erc20TokenAddresses`, `amountChanges`, and even `calldataHash` are absent from what the wallet owner cryptographically committed to.
- `dimensionsCheck` only forces internal consistency of the *new* `circomData` (`erc20TokenAddresses.length == dimensions.tokenNumber`, etc.) [2](#0-1) , it does not compare against any previously-signed dimensions.
- `formInputForCircom` routes to `formInputEmporiumMin` whenever `erc20TokenAddresses.length == 0` [3](#0-2) , producing only `[emporiumMessage, timeStamp, calldataHash]` as public input, none of which is bound to `stack.ops`, tokens, or balances.
- `MainEVMCircuitMin` never references `outTimeStamp` or `calldataHash` in any constraint - `message` is simply `Poseidon(messageSeed)`, unconnected to the declared public inputs [4](#0-3) . An attacker can therefore synthesize a valid Groth16 proof for arbitrary `emporiumMessage`/`calldataHash`/`timeStamp` values at will.
- `buildVerifierId` derives the verifier purely from `dimensions` + `externalActionId` [5](#0-4) , so setting `dimensions.tokenNumber = 0` deterministically selects the Min verifier.
- `Hinkal.transact`'s balance/slippage-diff loop is bound by `circomData.erc20TokenAddresses.length` [6](#0-5) ; with an empty array this loop is a no-op, so no accounting whatsoever applies to any token moved by the ops.
- `EmporiumUpgradeable.runAction` decodes and executes `stack.ops` unconditionally, independent of `circomData.erc20TokenAddresses.length`, including `CASE 1` stateful `callHinkalWallet` invocations [7](#0-6) ; its own `balancesBefore`/`balancesAfter`/UTXO-creation logic is likewise bound only by `circomData.erc20TokenAddresses.length` [8](#0-7) , so with an empty array it silently skips all balance checks and UTXO minting while the ops still ran.

Exploit flow: attacker observes/obtains a valid `EmporiumStack` (`signerAddress`, `ops`, `v,r,s`, `maxFee`, `deadline`) that a wallet owner signed intending a real token-moving transaction with `erc20TokenAddresses.length > 0`. Attacker builds a new `circomData` with identical `externalActionData.externalActionMetadata` (same signed stack) but `erc20TokenAddresses = []`, matching empty `slippageValues`/`onChainCreation`/`inputNullifiers`/`outCommitments`/`encryptedOutputs` (satisfying `dimensionsCheck`), computes its own self-consistent `calldataHash`, and generates a trivial Min-circuit proof. Calling `Hinkal.transact` with `dimensions.tokenNumber = 0` selects the Min verifier, passes `performHinkalChecks`, and `runAction` executes the owner's signed `stack.ops` (which can call `IHinkalWallet.callHinkalWallet`/`doSendToRelay`) with no balance equation ever checked, and no UTXO minted for whatever tokens moved.

### Impact Explanation
The wallet owner's authorized fund-moving operations execute, but the Hinkal ledger (balance diff checks in `Hinkal.transact` and UTXO minting in `EmporiumUpgradeable.runAction`) never accounts for them because both are gated by `erc20TokenAddresses.length`, which the attacker set to zero. Any tokens the ops pull from the wallet or that land in the Emporium contract are unaccounted for - a shielded receipt is never created, meaning value is effectively lost from the user's perspective while it left the wallet. This is a proof/verification-coverage bypass causing execution of wallet-authorized calls whose token effects the accepted proof never constrained, and is repeatable against any wallet owner who signs Emporium operations for token transfers, matching the Critical category (execution of fund-moving calls under a proof that never constrained the fields those calls depend on, and effectively permanent freezing/loss of the moved funds since no compensating UTXO is minted).

### Likelihood Explanation
Preconditions: a wallet owner must have produced a valid `EmporiumStack` signature (an ordinary/expected usage pattern of the protocol) for ops that move tokens; the attacker only needs to see that signed payload (it becomes part of public calldata once submitted, or shared with any relay) and resubmit it with a different `circomData`/`dimensions` and a freely-generated Min proof. No privileged role, no compromised owner keys, and no dependence on relay/node misbehavior are required - the attacker is a purely unprivileged actor exploiting the fact that the signature scope and the proof scope for the "Min" path are both narrower than what actually executes. This is repeatable for every such signed stack that reaches on-chain visibility before being consumed by its intended full-path call.

### Recommendation
Bind the EIP-712 `EmporiumSignature` (and/or the Min circuit's public inputs) to the full `Dimensions`/`erc20TokenAddresses`/`calldataHash` context so a signature/proof scoped for one dimension cannot be replayed under another. At minimum, reject `formInputEmporiumMin`/the Min verifier path whenever `stack.ops` is non-empty or contains any `invokeWallet`/token-moving operation, and make `verifyWallet`'s signed payload include `circomData.calldataHash` (which already commits to `erc20TokenAddresses.length` via `dimensionsCheck`-enforced array lengths) so the signature is dimension-specific.

### Proof of Concept
Hardhat test:
1. Deploy `Hinkal`, `HinkalHelper`, `VerifierFacade` with both the Normal and Min verifiers registered (Min registered under `Dimensions(0,0,0)` + Emporium `externalActionId`).
2. Have a "wallet owner" EOA sign a valid `EmporiumStack` (`ops` containing a `callHinkalWallet` call to `doSendToRelay` moving real ERC20 balance out of an `IHinkalWallet` mock, `signerAddress = ownerAddr`).
3. Craft `circomData` with `erc20TokenAddresses = []`, `slippageValues/onChainCreation/inputNullifiers/outCommitments/encryptedOutputs = []`, `externalActionData.externalActionMetadata = abi.encode(stack)`, and a self-consistent `calldataHash = getHashedCalldata(circomData)`.
4. Generate a Min-circuit Groth16 proof for public input `[emporiumMessage, timeStamp, calldataHash]` using an arbitrary `messageSeed` (no relation required to any UTXO).
5. Call `Hinkal.transact(a,b,c, Dimensions(0,0,0), circomData)` and assert it succeeds, `usedMessages[emporiumMessage]` becomes true, and the ERC20 tokens leave the wallet mock (via `doSendToRelay`) with `getBalancesForArray` never invoked/checked for that token and no UTXO commitment inserted for the moved value - proving the balance equation (`balancesBefore`/`balancesAfter`, `balanceDif == amountChanges[i] + utxoAmount`) was never evaluated for the token the ops actually moved.

### Citations

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L318-328)
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
```

**File:** contracts/HinkalHelper.sol (L64-90)
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

**File:** circuits/MainEVMCircuitMin.circom (L6-18)
```text
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

**File:** contracts/VerifierFacade.sol (L28-43)
```text
    function buildVerifierId(
        Dimensions calldata dimensions,
        uint256 externalActionId
    ) public pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        dimensions.tokenNumber,
                        dimensions.nullifierAmount,
                        dimensions.outputAmount,
                        externalActionId
                    )
                )
            );
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
