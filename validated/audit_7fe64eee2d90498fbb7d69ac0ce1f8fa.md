### Title
Min-path Emporium action bypasses all balance/signature accounting, enabling theft of any token balance held by Emporium - (File: `contracts/CircomDataBuilder.sol`, `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`, `contracts/Hinkal.sol`)

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, which only proves `message == Poseidon(messageSeed)` via `MainEVMCircuitMin` — no root, no nullifiers, no amounts are constrained. Because `erc20TokenAddresses` is empty, both `EmporiumUpgradeable.runAction`'s internal balance loop and `Hinkal.transact`'s outer balance-invariant loop are entirely skipped, while `EmporiumStack.ops` still runs fully attacker-controlled external calls (`op.endpoint.call{value: op.value}(op.callData)`) with `signerAddress == address(0)` bypassing EIP‑712 signature verification too.

### Finding Description
The broken equality is: **assets Emporium can move in a transaction == assets accounted for in `balancesBefore`/`balancesAfter`**.

- `CircomDataBuilder.formInputForCircom` selects `formInputEmporiumMin` whenever `erc20TokenAddresses.length == 0` for the Emporium action id: [1](#0-0) . `formInputEmporiumMin` only feeds `emporiumMessage`, `timeStamp`, `calldataHash` as public inputs [2](#0-1) , matching `MainEVMCircuitMin`, which constrains nothing except `message <== Poseidon(1)([messageSeed])` [3](#0-2) .
- `HinkalHelper.dimensionsCheck` forces `amountChanges.length == erc20TokenAddresses.length == dimensions.tokenNumber`, so with an empty token list, `amountChanges`, `inputNullifiers`, `outCommitments` are all empty too [4](#0-3) .
- In `Hinkal.transact`, the balance-invariant loop (`balanceDif == amountChanges[i] + utxoAmount`) iterates only over `circomData.erc20TokenAddresses`, i.e. zero iterations, so no accounting whatsoever occurs at the entrypoint level [5](#0-4) .
- Inside `EmporiumUpgradeable.runAction`, `balancesBefore`/`balancesAfter` are likewise computed only over the (empty) `circomData.erc20TokenAddresses`, so the `BalanceChangeShouldBePositive` check and UTXO creation logic never execute for any token [6](#0-5) .
- Meanwhile the `ops` loop unconditionally executes regardless of `erc20TokenAddresses.length`: with `stack.signerAddress == address(0)`, `verifyWallet` returns immediately after marking `usedMessages`, entirely skipping ECDSA signature verification [7](#0-6) , and each stateless op executes `op.endpoint.call{value: op.value}(op.callData)` against an attacker-chosen endpoint/calldata (only `callHinkalWallet`/`doSendToRelay` selectors are blocked) [8](#0-7) .

Any unprivileged EOA can therefore call `Hinkal.transact` with a trivially-generated Min proof (they know their own `messageSeed`), any valid historical `rootHashHinkal` (irrelevant since it is unused/unconstrained on this path — no nullifiers are spent), `erc20TokenAddresses = []`, and an `externalActionMetadata` decoding to an `EmporiumStack` with `signerAddress = 0` and `ops` calling any ERC20 token's `transfer`, any router, or any contract, from Emporium's own address as `msg.sender`. Since `erc20TokenAddresses` is empty, no balance check anywhere in the call stack (`Hinkal.transact`, `EmporiumUpgradeable.runAction`) will detect or revert on funds leaving the Emporium contract. This directly targets any ETH or ERC20 balance the Emporium contract holds (e.g., from `receive()` accepting ETH, or ERC20 tokens transferred into it during prior `_externalTransact` deposit flows where `deltaAmountChanges[i] < 0`, particularly stray/unswept balances left over from multi-hop swap ops that produce a token not included in that transaction's declared `erc20TokenAddresses`).

### Impact Explanation
An attacker can drain any ERC20 or ETH balance currently held by the Emporium contract with zero signature verification and zero on-chain accounting, using only a trivially self-satisfiable "Min" proof. This is direct theft of shielded/in-flight user or protocol funds parked at the Emporium contract address, matching the Critical severity category ("direct theft of shielded or in-flight user funds"). The attack is repeatable against any balance that subsequently accrues on Emporium.

### Likelihood Explanation
Preconditions: the attacker needs Emporium to hold a non-zero balance of some asset (ETH via `receive()`, or ERC20 residue from swap-style ops that convert into a token not declared in that transaction's `erc20TokenAddresses`, or otherwise). No signature, no root/nullifier validity relative to the target funds, and no privileged role is required — the attacker only needs to be able to call `Hinkal.transact` and supply a self-generated Min proof, which is always achievable by any unprivileged EOA. This makes the attack highly feasible and repeatable whenever the Emporium contract accumulates any stray balance.

### Recommendation
Do not allow the "Min" fast-path to be paired with arbitrary `EmporiumStack.ops` execution. Either: (1) require `formInputEmporiumMin`/Min-proof transactions to disallow any `ops` entries that make external calls (only allow no-op / message-attestation use), or (2) make `EmporiumUpgradeable.runAction`'s balance accounting independent of `circomData.erc20TokenAddresses` — track and require zero net balance change (across all tokens actually touched, not just the declared list) whenever the Min path is used, or (3) forbid `erc20TokenAddresses.length == 0` combined with non-empty `ops`/non-empty `callData` entirely at the `formInputForCircom` dispatch or in `EmporiumUpgradeable.runAction`.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, register Emporium as external action and as allowed recipient.
2. Fund the Emporium contract directly with ETH and/or an ERC20 token (simulate residual balance from a prior legitimate op/swap or direct transfer), asserting `balanceBefore = X`.
3. As an unprivileged attacker EOA, construct `CircomData` with `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `erc20TokenAddresses = []`, `amountChanges = []`, `inputNullifiers = []`, `outCommitments = []`, valid `rootHashHinkal`/index, and `externalActionMetadata` = ABI-encoded `EmporiumStack{ signerAddress: address(0), ops: [{endpoint: token, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, X))}] }`.
4. Generate a locally-produced Groth16 proof for `MainEVMCircuitMin` using an attacker-chosen `messageSeed` (trivial, no dependency on any UTXO/root).
5. Call `Hinkal.transact(a, b, c, dimensions, circomData)` from the attacker EOA.
6. Assert: call succeeds without reverting on any balance check; `token.balanceOf(attacker)` increases by `X`; `token.balanceOf(Emporium)` decreases by `X`; assert the equality `balancesBefore[i] == balancesAfter[i]` (over `circomData.erc20TokenAddresses`, which is empty) trivially holds `0==0` while the real external balance moved by `X`, proving the accounting invariant is broken.

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

**File:** contracts/Hinkal.sol (L88-147)
```text
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
            }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-151)
```text
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
