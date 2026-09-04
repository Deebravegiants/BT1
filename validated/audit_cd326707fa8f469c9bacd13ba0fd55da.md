### Title
Emporium's arbitrary `endpoint.call` in "stateless" mode lets a prover drain any ERC20 balance the Emporium contract holds via `transferFrom(self, attacker, amt)`, since the token isn't required to be in the checked `erc20TokenAddresses` set - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` executes attacker-supplied `EmporiumOperation`s via raw `.call()` from the Emporium contract's own address. When `stack.signerAddress == address(0)`, `verifyWallet` skips signature verification entirely and only the pre/post-balance check on the explicit `circomData.erc20TokenAddresses` array constrains outcomes. Any token not included in that array is completely unconstrained, so an attacker can direct a `transferFrom(address(this), attacker, balance)` call at a WETH-style token the Emporium holds a balance of, exactly mirroring the RubiconMarket `this.offer` bug class (message call self-authorizes on tokens whose `transferFrom` skips the allowance check when `src == msg.sender`).

### Finding Description
`runAction` decodes attacker-controlled `externalActionMetadata` into an `EmporiumStack` and, for "Stateless Interaction" ops (`invokeWallet == false`), executes: [1](#0-0) 

`msg.sender` inside that call is the Emporium contract itself, just like `this.offer` made `msg.sender == RubiconMarket` in the referenced report. If `signerAddress == address(0)`, `verifyWallet` returns immediately without checking any signature over the `ops` array: [2](#0-1) 

The only safety net is the pre/post balance-delta check, but it is scoped exclusively to `circomData.erc20TokenAddresses`: [3](#0-2) [4](#0-3) 

An attacker crafts an op with `endpoint = <target ERC20>` and `callData = transferFrom(address(emporium), attacker, amount)`, and simply omits that ERC20 from `circomData.erc20TokenAddresses`. Because that token's balance is never sampled before/after, the invariant `balanceChange == -deltaAmountChanges[i] (for tracked tokens only)` cannot detect or block the drain. On a token whose `transferFrom` does not require allowance when `src == msg.sender` (WETH-style semantics, as cited in the external report), the call succeeds even though the Emporium never approved itself, and the funds go straight to the attacker.

While `externalActionMetadata` is committed inside `calldataHash`, which is itself a public input verified by the ZK proof [5](#0-4) [6](#0-5) , that only proves the transaction was crafted by whoever generated the proof — it does not constrain which `endpoint`/`callData`/tokens are targeted, nor does it tie the outflow to the balance-equality check for tokens outside the declared array. Any unprivileged EOA holding any valid (even trivially small) UTXO can generate such a proof and call `Hinkal.transact` with the crafted `externalActionData`, since `runAction` is reachable via `Hinkal._externalTransact` → `IExternalActionV2(...).runAction(...)`: [7](#0-6) 

This breaks the intended balance equation for external actions ("total change of emporium balance = what was moved to emporium + how emporium balance changed through tx") because that equation is only enforced per-token for tokens explicitly listed by the attacker, allowing theft of Emporium's balance in any token left off that list — including protocol/relay fees, dust, or other users' funds that happen to be resting in the shared Emporium contract (e.g., from partially-processed or fee-related flows).

### Impact Explanation
This is a direct theft of funds held by the Emporium external-action contract — a shared, protocol-operated contract that can hold ERC20/ETH balances belonging to the protocol (fees) or transiently to other users. An attacker can move any WETH-style token's entire Emporium balance to themselves without any authorization check on that specific transfer, since the token is simply excluded from the checked-token array. This qualifies as Critical/High under "direct theft of shielded or in-flight user funds" / "theft ... of protocol/relay fees" and "executing calls or moving assets ... never authorised" (the Emporium contract itself never authorized the self-transfer).

### Likelihood Explanation
Likelihood is moderate-to-high for any deployment where the Emporium contract accrues balances of tokens with WETH-style `transferFrom` self-authorization semantics (a documented, non-exotic pattern per the referenced report), or wherever leftover balances (fees, dust, failed-op remnants) sit in the Emporium between transactions. The attack requires only a valid ZK proof over the attacker's own (arbitrarily small) UTXO set plus knowledge of the balance-check gap — no privileged role, relay, or other user's key is needed.

### Recommendation
- Enumerate and check balances for every unique token address referenced by any `op.endpoint`/decoded `callData` in the `EmporiumStack`, not just `circomData.erc20TokenAddresses`, before allowing `signerAddress == address(0)` stateless calls.
- Alternatively, disallow raw `endpoint.call` targets that match known ERC20 selectors (`transfer`, `transferFrom`, `approve`) unless the token is explicitly included and balance-checked in `circomData.erc20TokenAddresses`.
- Consider requiring `stack.signerAddress != address(0)` (i.e., routing through `HinkalWallet`, which restricts sensitive selectors) for any operation, removing the fully-unauthenticated "stateless" `address(0)` bypass in `verifyWallet`.

### Proof of Concept
1. Attacker holds a small valid Hinkal UTXO and can generate a valid proof for `Hinkal.transact`.
2. Attacker sets `circomData.externalActionData = {externalAddress: Emporium, externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalActionMetadata: abi.encode(EmporiumStack{signerAddress: address(0), ops: [EmporiumOperation{endpoint: WETH, invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC20.transferFrom.selector, address(emporium), attacker, wethBalanceOfEmporium)}], maxFee: 0, deadline: type(uint256).max})}`.
3. Attacker sets `circomData.erc20TokenAddresses` to an unrelated/empty set (excluding WETH), so `deltaAmountChanges` for WETH is never computed and the pre/post balance check in `runAction` never samples WETH.
4. Attacker calls `Hinkal.transact(...)`, which reaches `EmporiumUpgradeable.runAction` → `verifyWallet` returns immediately (`signerAddress == address(0)`) → the loop executes `WETH.call(transferFrom(emporium, attacker, wethBalanceOfEmporium))`, succeeding because WETH's `transferFrom` allows `src == msg.sender` without allowance [8](#0-7) .
5. `runAction` completes without reverting since the balance-change check never inspects WETH, and the attacker has drained Emporium's WETH balance.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-87)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L97-118)
```text
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

**File:** contracts/CircomDataBuilder.sol (L10-18)
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
```

**File:** contracts/CircomDataBuilder.sol (L180-234)
```text
    function formBasicInput(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData,
        uint256[] memory input,
        uint256 index,
        uint256 emporiumMessage
    ) internal pure returns (uint256[] memory) {
        // 1) First we list public inputs as in the body of the main template (not the one with exact dimensions)
        input[index++] = circomData.stealthAddressStructure.H1x;
        input[index++] = circomData.stealthAddressStructure.H1y;
        input[index++] = circomData.stealthAddressStructure.stealthAddress;
        input[index++] = emporiumMessage; // this is for Emporium message signature verification

        // 2) Then we list the private inputs as in the body of the main template
        input[index++] = circomData.rootHashHinkal;
        input[index++] = getSignedMessageHash(
            chainId,
            verifyingContract,
            circomData,
            emporiumMessage
        );

        for (uint16 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            input[index++] = uint256(
                uint160(circomData.erc20TokenAddresses[i])
            );
        }

        for (uint16 i = 0; i < circomData.amountChanges.length; i++) {
            require(
                circomData.amountChanges[i] < MAX_AMOUNT &&
                    circomData.amountChanges[i] > -1 * MAX_AMOUNT,
                "amount changed is too large"
            );

            input[index++] = circomData.amountChanges[i] >= 0
                ? uint256(circomData.amountChanges[i])
                : CIRCOM_P - uint256(-circomData.amountChanges[i]);
        }

        for (uint16 i = 0; i < circomData.inputNullifiers.length; i++) {
            for (uint16 j = 0; j < circomData.inputNullifiers[i].length; j++) {
                input[index++] = circomData.inputNullifiers[i][j];
            }
        }

        input[index++] = circomData.timeStamp;

        for (uint16 i = 0; i < circomData.outCommitments.length; i++) {
            for (uint16 j = 0; j < circomData.outCommitments[i].length; j++) {
                input[index++] = circomData.outCommitments[i][j];
            }
        }
        input[index++] = circomData.calldataHash;
```

**File:** contracts/Hinkal.sol (L232-261)
```text
    ///@notice internal function to use Hinkal with external contracts.
    ///@param circomData circom data.
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
