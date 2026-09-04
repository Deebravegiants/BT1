## Title
Emporium relay/protocol fee is charged on the pre-execution withdrawal amount, not on the actual post-execution balance change, letting arbitrary op profit bypass the fee entirely - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction()` withdraws a ZK-proven amount (`deltaAmountChanges`) from the user's shielded balance to fund a user-supplied stack of arbitrary calls (`stack.ops`), then converts whatever ends up in the contract afterward back into a new private UTXO for the user via `handleOut`. The relay/protocol fee, however, is computed in `payRelayFees` strictly from the pre-execution `deltaAmountChanges` (the amount the circuit committed to move), not from the actual `balanceChange` measured after the ops run. Any extra value the ops generate is fee-free.

### Finding Description
`runAction` records `balancesBefore`, runs the caller-supplied `stack.ops` (arbitrary external calls, or wallet calls when `stack.signerAddress != address(0)`), then calls `payRelayFees(circomData, stack.signerAddress, deltaAmountChanges)` **before** computing the real result of those ops: [1](#0-0) 

`payRelayFees` only iterates on `deltaAmountChanges` (the amounts already proven/withdrawn via the circuit) to compute `sumAbs` and the resulting `relayFee`; it never looks at `balancesAfter`/`balancesBefore`: [2](#0-1) 

After fees are settled, the *actual* post-execution `balanceChange` (which can exceed what was withdrawn, e.g. due to arbitrage, favorable swap execution inside an op, or any other value the ops manage to pull into the Emporium contract) is computed and handed to `handleOut`, which sends the **entire** surplus back to the user and re-mints it as a brand-new, unfee'd shielded UTXO: [3](#0-2) 

This is the direct analog of the Illuminate M-2 report: the fee is calculated on the amount declared/committed ahead of time (`lent`/`deltaAmountChanges`), while the true economic result of executing the actions (`premium`/`balanceChange`) is measured only afterward and is never subjected to the fee. Compare with `ExternalActionSwap.sol`, where the equivalent bug was already fixed correctly — there, `hinkalFee` is computed on `swappedAmount`, i.e. the *actual* output of the router call, not the input amount: [4](#0-3) 

In `EmporiumUpgradeable`, no equivalent post-execution fee exists. A user can withdraw a small amount from their shielded balance (paying a fee only on that small amount), and structure `stack.ops` so that the Emporium contract ends up holding materially more of a given token than was withdrawn (e.g., by having one of the stateless ops pull additional funds the user controls into the Emporium contract, or by capturing positive slippage/arbitrage profit from a DEX call). `payRelayFees` fees only the declared negative `deltaAmountChanges[i]`; the surplus captured in `balanceChange` is converted 1:1 into a new private UTXO via `handleOut` with zero relay/protocol fee.

### Impact Explanation
This results in permanent loss of protocol/relay fee revenue: any value routed through Emporium beyond the amount explicitly declared in the ZK-proven `deltaAmountChanges` is laundered into the shielded pool completely fee-free, regardless of its size. This matches the "High - theft or permanent freezing of protocol/relay fees" impact category, since the relay/protocol is structurally unable to collect its variable-rate fee on this class of value transfer.

### Likelihood Explanation
The `signerAddress == address(0)` (self-executed / stateless) path requires no signature or relayer cooperation — any unprivileged EOA that can pass `onlyAllowedRecipient` (i.e., call through Hinkal → Emporium) can construct `stack.ops` freely, as `verifyWallet` skips all checks when `stack.signerAddress == address(0)`: [5](#0-4) 
Any user who can get extra token balance into the Emporium contract during op execution (their own pre-approved tokens, a favorable swap/arbitrage call, etc.) triggers this fee-bypass every time, with no economic barrier beyond gas.

### Recommendation
Compute the relay/protocol fee from the actual measured `balanceChange` after the ops execute (the same value used in `handleOut`), not from the pre-execution `deltaAmountChanges`. Concretely, move `payRelayFees` after the `balanceChange` computation and apply the variable rate to the full outgoing `balanceChange` for each token, consistent with how `ExternalActionSwap.sol` fees the real `swappedAmount`.

### Proof of Concept
1. User has a normal ERC20 token balance in their own EOA and pre-approves the `EmporiumUpgradeable` contract to `transferFrom` a large amount.
2. User calls Hinkal's transact flow routing to Emporium (`externalActionId` set to Emporium), with `signerAddress == address(0)`, `circomData.erc20TokenAddresses = [tokenA]`, `deltaAmountChanges[0]` a small negative withdrawal (e.g. 1 wei) from their shielded balance — paying a negligible fee.
3. `stack.ops` includes one stateless op calling `tokenA.transferFrom(userEOA, EmporiumUpgradeable_address, largeAmount)`.
4. `payRelayFees` charges fee only on the 1-wei `deltaAmountChanges[0]`.
5. `balanceChange` for `tokenA` = `largeAmount + 1 (approx)`; `handleOut` sends this whole amount back and mints a new private UTXO for the user with the full `largeAmount` value included, with no fee applied to `largeAmount`. [6](#0-5)

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-184)
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

        if (utxoSetLength < circomData.erc20TokenAddresses.length) {
            utxoSet.skipLast(
                circomData.erc20TokenAddresses.length - utxoSetLength
            );
        }

        return utxoSet;
    }

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L201-245)
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
            } else {
                relayFee = flatFee;
            }

            payRelay(
                circomData.relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
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

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L63-91)
```text
        uint256 swappedAmount = callRouter(
            inputToken,
            inputAmount,
            outputToken,
            circomData.externalActionData.externalActionMetadata
        );

        uint256 relayFee = circomData.feeStructure.flatFee;

        uint256 hinkalFee = hinkalHelper.calculateRelayFee(
            swappedAmount,
            0,
            circomData.feeStructure.variableRate
        );

        if (circomData.feeStructure.feeToken == outputToken) {
            sendToRelay(circomData.relay, relayFee + hinkalFee, outputToken);
        } else {
            sendToRelay(
                circomData.relay,
                relayFee,
                circomData.feeStructure.feeToken
            );
            sendToRelay(circomData.relay, hinkalFee, outputToken);
        }

        uint256 totalFee = hinkalFee +
            (outputToken == circomData.feeStructure.feeToken ? relayFee : 0);
        uint256 amountToSendToHinkal = swappedAmount - totalFee;
```
