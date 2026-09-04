### Title
Emporium fee is charged only on the declared shielded withdrawal, not on value created by arbitrary Emporium operations - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction()` only charges the relay/protocol fee on the amount that the ZK proof declares as leaving the shielded pool (`deltaAmountChanges[i] < 0`). Any value that the attacker injects and converts during the arbitrary `EmporiumOperation` calls — using the attacker's own external, unshielded funds — is captured as a brand-new shielded UTXO via `handleOut()` completely fee-free. This mirrors the reported UNCX pattern: pay the fee on a minimal "lock" amount, then grow the position for free via `increaseLiquidity`.

### Finding Description
`payRelayFees()` in `EmporiumUpgradeable.sol` skips fee calculation for every token whose `deltaAmountChanges[i] >= 0` (comment: "tokens deposited into Emporium are not charged") and only assesses `calculateRelayFee` on the negative deltas — i.e. the amount the prover *declares* it is pulling out of the shielded balance: [1](#0-0) 

Immediately before that, `runAction()` executes arbitrary attacker-supplied `EmporiumOperation`s. In "Stateless Interaction" mode the Emporium contract itself makes an arbitrary external call with attacker-chosen `endpoint`/`callData`/`value`: [2](#0-1) 

Because the attacker (as their own EOA) can pre-approve Emporium to spend their own unrelated, non-shielded tokens, one of these ops can be `token.transferFrom(attacker, emporium, largeAmount)`, injecting external capital that never appears in `deltaAmountChanges`. A subsequent op can swap the combined balance (tiny declared shielded withdrawal + large injected capital) through a router. After the ops run, `payRelayFees` is computed purely from `deltaAmountChanges` (the tiny declared amount), and only afterward is the resulting balance delta captured: [3](#0-2) 

`handleOut()` then mints the *entire* post-ops balance increase (tiny withdrawal + injected capital + swap proceeds) into a new UTXO/on-chain commitment with no additional fee: [4](#0-3) 

The `deltaAmountChanges` and `feeStructure` values are indeed bound into the proof via `calldataHash`/circuit public inputs (`getHashedCalldata1`, `formBasicInput`) [5](#0-4) , so the attacker cannot forge these fields — but nothing forces the *declared* withdrawal (`amountChanges`/`deltaAmountChanges`) to reflect the true economic size of the operation. The prover freely chooses a minimal withdrawal amount while the bulk of the value transformation happens through externally-injected capital inside the ops loop, which the fee formula never sees.

### Impact Explanation
This breaks the intended balance/fee equality: relay/protocol fee revenue is supposed to be proportional to the value moved through a Hinkal-mediated transaction, but a user can direct the majority of value creation through the "free" (`deltaAmountChanges[i] >= 0`) path while declaring only a negligible amount on the fee-bearing path. This is a permanent, systematic loss of protocol/relay fee revenue on Emporium swaps/operations — matching the High-severity category "theft or permanent freezing of protocol/relay fees."

### Likelihood Explanation
Any unprivileged EOA holding tokens and willing to approve them to the Emporium contract can execute this: it requires only crafting a valid proof for a trivial declared withdrawal and structuring the `EmporiumOperation` list (which is entirely attacker-controlled and only integrity-checked, not economically checked) to route larger external capital through the same call. No relayer, admin, or oracle assumptions are needed, and no protocol invariant currently prevents it — this is highly likely to be exploited in practice by any relay-fee-averse user of Emporium.

### Recommendation
Compute the Emporium relay/protocol fee against the *total* net value created/consumed by the operation (i.e., the full `balanceChange` measured in `runAction`, matching what is ultimately minted via `handleOut`) rather than solely against the prover-declared `deltaAmountChanges`. Alternatively, require that any externally injected funds used inside `EmporiumOperation` calls be explicitly declared and fee-assessed as part of `amountChanges`/`deltaAmountChanges`, and reject/ignore any balance increase not attributable to a fee-assessed input.

### Proof of Concept
1. Attacker approves the `Emporium` contract to spend a large amount of `TOKEN_A` from their own wallet.
2. Attacker builds a `CircomData`/proof declaring `erc20TokenAddresses = [TOKEN_A]`, `amountChanges[0] = -1` (a 1-wei "withdrawal" from the shielded pool), so `deltaAmountChanges[0] = -1`.
3. `externalActionMetadata` encodes an `EmporiumStack` with two `EmporiumOperation`s:
   a. `TOKEN_A.transferFrom(attacker, emporium, largeAmount)` (stateless call, funded from attacker's own wallet — no shielded funds involved).
   b. A DEX router call swapping the Emporium's full `TOKEN_A` balance (1 wei + largeAmount) into `TOKEN_B`.
4. `runAction()` executes both ops, then calls `payRelayFees`, which only computes fee on the declared `-1` wei delta for `TOKEN_A` (negligible/zero fee) — see `EmporiumUpgradeable.sol:201-234`.
5. `handleOut()` mints a new shielded UTXO of the full `TOKEN_B` swap proceeds (`balancesAfter - balancesBefore`) — see `EmporiumUpgradeable.sol:162-184` — with zero protocol/relay fee taken on that (large) amount.
6. Repeat at scale: the relay/protocol permanently loses fee revenue on every swap/value-transformation an attacker chooses to route this way.

### Citations

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-160)
```text
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

        if (utxoSetLength < circomData.erc20TokenAddresses.length) {
            utxoSet.skipLast(
                circomData.erc20TokenAddresses.length - utxoSetLength
            );
        }

        return utxoSet;
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L162-184)
```text
    function handleOut(
        int256 balanceChange,
        CircomData calldata circomData,
        uint256 i
    ) internal returns (UTXO memory outUtxo) {
        // total change can be less than zero if there was some balance before the call -> that's why we have <=
        if (balanceChange <= 0) {
            return outUtxo;
        }

        transferERC20TokenOrETH(
            circomData.erc20TokenAddresses[i],
            msg.sender,
            uint256(balanceChange)
        );

        outUtxo = UTXO(
            uint256(balanceChange),
            circomData.erc20TokenAddresses[i],
            circomData.stealthAddressStructure,
            circomData.timeStamp
        );
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L201-234)
```text
    function payRelayFees(
        CircomData calldata circomData,
        address signerAddress,
        int256[] calldata deltaAmountChanges
    ) internal {
        FeeStructure calldata feeStructure = circomData.feeStructure;

        bool foundToken = false;

        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            // tokens deposited into Emporium are not charged
            if (deltaAmountChanges[i] >= 0) {
                continue;
            }

            address erc20TokenAddress = circomData.erc20TokenAddresses[i];
            bool isFeeToken = erc20TokenAddress == feeStructure.feeToken;

            if (isFeeToken) {
                foundToken = true;
            }

            uint256 relayFee = 0;
            uint256 flatFee = isFeeToken ? feeStructure.flatFee : 0;

            if (signerAddress == address(0)) {
                uint256 sumAbs = uint256(-deltaAmountChanges[i]);

                EmporiumStorageVars storage $ = _getEmporiumStorage();
                relayFee = $._hinkalHelper.calculateRelayFee(
                    sumAbs,
                    flatFee,
                    feeStructure.variableRate
                );
```

**File:** contracts/CircomDataBuilder.sol (L10-35)
```text
    function getHashedCalldata(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        // because of stack too deep error, we need to split the calldata into two parts
        uint256 calldataHash1 = getHashedCalldata1(circomData);
        uint256 calldataHash2 = getHashedCalldata2(circomData);
        return (uint256(keccak256(abi.encode(calldataHash1, calldataHash2))) %
            CIRCOM_P);
    }

    function getHashedCalldata1(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.publicSignalCount,
                        circomData.relay,
                        circomData.emporiumMessage,
                        circomData.externalActionData,
                        circomData.slippageValues
                    )
                )
            );
    }
```
