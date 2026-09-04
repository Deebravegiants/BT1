### Title
Emporium ERC20 balance can be drained via `signerAddress == address(0)` + `MainEVMCircuitMin` path bypassing all value-conservation checks - (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
When `Dimensions.tokenNumber == 0` and the external action is `HINKAL_EMPORIUM_ACTION_ID`, `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin`, whose only real circuit constraint is `message == Poseidon(1)([messageSeed])` with an attacker-chosen `messageSeed`. This proof carries no authorization semantics, yet it is accepted by `Hinkal.transact` for an `EmporiumStack{signerAddress: address(0)}` whose `verifyWallet` performs no signature check at all. Because `circomData.erc20TokenAddresses` is empty, every balance-conservation loop in both `Hinkal.transact` and `EmporiumUpgradeable.runAction` iterates zero times, so an arbitrary ERC20 transfer executed by an Emporium-issued `op.endpoint.call(op.callData)` is never checked against any accounted amount.

### Finding Description
The broken equality: **set of tokens whose Emporium ERC20 balance actually changes** (`op.endpoint.call(abi.encodeCall(IERC20.transfer, ...))`, arbitrary token) **!=** **set of tokens iterated by the value-conservation loops** (`circomData.erc20TokenAddresses`, empty by construction).

Path:
1. `CircomDataBuilder.formInputForCircom` [1](#0-0)  routes to `formInputEmporiumMin` when `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`, producing only `[emporiumMessage, timeStamp, calldataHash]` as public input [2](#0-1) .
2. `MainEVMCircuitMin` constrains solely `message <== Poseidon(1)([messageSeed])` [3](#0-2) , with `messageSeed` a private witness the attacker picks freely, so any `emporiumMessage` value can be trivially "proven".
3. `dimensionsCheck` only requires `erc20TokenAddresses.length == dimensions.tokenNumber` [4](#0-3) , so `tokenNumber:0` is fully self-consistent and passes.
4. `Hinkal.transact`'s balance-conservation loop over `circomData.erc20TokenAddresses` [5](#0-4)  iterates zero times when the array is empty — `balanceDif == amountChanges + utxoAmount` is never evaluated for any token.
5. `_externalTransact` calls `EmporiumUpgradeable.runAction` with `deltaAmountChanges` also of length 0 [6](#0-5) .
6. `EmporiumUpgradeable.verifyWallet`, for `stack.signerAddress == address(0)`, only checks/marks `usedMessages[emporiumMessage]` and returns — no signature check [7](#0-6) .
7. The `ops` loop then executes `op.endpoint.call(op.callData)` with `msg.sender == Emporium` for attacker-supplied `endpoint`/`callData`, e.g. `IERC20.transfer(attacker, balanceOf(Emporium))` on a token Emporium holds [8](#0-7) .
8. The post-call balance-conservation loop in `runAction` also iterates over `circomData.erc20TokenAddresses` (empty), so `BalanceChangeShouldBePositive` is never checked for the drained token [9](#0-8) .

No existing guard (`performHinkalChecks`, `dimensionsCheck`, `verifyProof`, `rootHashExists`, `verifyWallet`, `nonReentrant`) constrains the actual token(s) touched by `op.callData` to the (empty) `erc20TokenAddresses` set. The comment "the only case when balanceChange can be < 0, when there were some funds on emporium before the call" confirms Emporium is expected to sometimes hold residual ERC20 balance between transactions (e.g., relay-fee rounding dust), giving the attacker a real target balance to steal.

### Impact Explanation
Critical: any unprivileged EOA can drain any ERC20 balance resting in the Emporium contract (fee dust, rounding remainders, or any token left there by prior legitimate flows) to itself, with zero collateral and zero legitimate authorization, by self-generating a trivial `MainEVMCircuitMin` proof and crafting the `EmporiumStack`. This is repeatable for any token/amount Emporium subsequently accumulates.

### Likelihood Explanation
Preconditions: Emporium must hold a nonzero ERC20 balance (realistic given fee/dust behavior implied by the code's own comments) and a verifier must be registered for the `tokenNumber:0` / `HINKAL_EMPORIUM_ACTION_ID` `verifierId` (the dedicated `MainEVMCircuitMin` circuit's existence indicates this path is an intended, deployed feature). Attacker cost is minimal (gas + trivial local proof generation, no deposit required). Fully repeatable each time Emporium accrues balance.

### Recommendation
Do not allow `formInputEmporiumMin`/`MainEVMCircuitMin` (empty `erc20TokenAddresses`) to be combined with a `signerAddress == address(0)` `EmporiumStack` that performs stateless calls capable of moving arbitrary ERC20 balances. Either: (1) require `erc20TokenAddresses` to include every token touched by `stack.ops` even when using the Min circuit path so balance-conservation loops actually execute, or (2) require a valid signature (non-zero `signerAddress`) for any op set that can transfer tokens out of Emporium, restricting the zero-signer path to genuinely stateless/no-value operations, or (3) add an explicit invariant check in `EmporiumUpgradeable.runAction` that Emporium's balance for every ERC20 it holds is non-decreasing (beyond the accounted `erc20TokenAddresses`) regardless of dimension/circuit variant used.

### Proof of Concept
Foundry fork test:
1. Deploy Hinkal + Emporium, register `HINKAL_EMPORIUM_ACTION_ID -> Emporium` in `externalActionMap`, register a verifier for `buildVerifierId({tokenNumber:0,...}, HINKAL_EMPORIUM_ACTION_ID)` pointing at the `MainEVMCircuitMin` verifier.
2. Seed Emporium with an ERC20 balance (e.g., transfer tokens directly, or run a legit Emporium flow that leaves dust).
3. As an unprivileged EOA, pick `messageSeed`, compute `message = Poseidon(1)([messageSeed])`, set `circomData.emporiumMessage = message`, generate the Groth16 proof for `MainEVMCircuitMin` with public inputs `[emporiumMessage, timeStamp, calldataHash]`.
4. Build `circomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `onChainCreation = []`, `slippageValues = []`, `externalActionData = {externalAddress: Emporium, externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalActionMetadata: abi.encode(EmporiumStack{signerAddress: address(0), ops: [{endpoint: token, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, tokenBalanceOf(Emporium)))}], maxFee:0, deadline:0})}`, computing `calldataHash` accordingly.
5. Call `Hinkal.transact(a, b, c, {tokenNumber:0,...}, circomData)` from the attacker EOA.
6. Assert: `token.balanceOf(Emporium)` before > 0, after == 0; `token.balanceOf(attacker)` increased by the stolen amount; and trace shows `balancesBefore.length == balancesAfter.length == 0` in `Hinkal.transact` and in `EmporiumUpgradeable.runAction`, i.e., no `balanceDif`/`BalanceChangeShouldBePositive` check ever fired for the stolen token.

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
