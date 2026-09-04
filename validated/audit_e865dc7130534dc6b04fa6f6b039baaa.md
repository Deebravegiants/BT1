### Title
Emporium EIP-712 signature omits `stealthAddressStructure`/`erc20TokenAddresses` binding, letting anyone who observes a signed `EmporiumStack` redirect the resulting shielded output to themselves - (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.verifyWallet` recovers `stack.signerAddress` from `EMPORIUM_SIGNATURE_TYPEHASH(emporiumMessage, opsHash, maxFee, deadline)` only, while `runAction`/`handleOut` attribute the resulting balance change (pulled by executing the signed `ops` against the signer's `HinkalWallet`) to `circomData.erc20TokenAddresses[i]` and mint the shielded proceeds to `circomData.stealthAddressStructure` — neither of which is part of the signed digest. Any party who obtains a valid `(v,r,s)` over a given `emporiumMessage`/`ops`/`maxFee`/`deadline` (which must be transmitted off-chain to whoever calls `Hinkal.transact` to execute it) can resubmit it with their own `stealthAddressStructure`/`erc20TokenAddresses`, causing the signer's wallet-authorized action to pay out to the submitter instead of the signer.

### Finding Description
Broken equality: the signer's authorization is claimed to cover "which ops run AND where the resulting funds go," but the EIP-712 hash only covers the former.

- `EMPORIUM_SIGNATURE_TYPEHASH` binds `circomData.emporiumMessage`, `_hashEmporiumOps(stack.ops)`, `stack.maxFee`, `stack.deadline`: [1](#0-0) 
- Meanwhile the destination/attribution of the resulting UTXO is entirely determined by attacker-supplied, unsigned `CircomData` fields:
  - `getBalancesForArray(circomData.erc20TokenAddresses)` picks which token's before/after balance of the Emporium contract is diffed: [2](#0-1) 
  - `handleOut` mints the resulting balance change into a UTXO addressed to `circomData.stealthAddressStructure`: [3](#0-2) 
- The stealth address and `erc20TokenAddresses`/`amountChanges` are only constrained by the ZK proof's public inputs (`formBasicInput`), which merely prove the *prover's own* spending-key relation to that stealth address — they carry no binding to `stack.signerAddress` at all: [4](#0-3) 
- `stack.ops[i].endpoint`/`callData`/`value` are executed through the signer's dedicated `HinkalWallet`, which only checks `onlyEmporium` (i.e. any caller of Emporium can trigger it, not just the signer/original submitter): [5](#0-4) 

Exploit flow: a signer produces `(v,r,s)` for a legitimate operation (e.g., claim rewards / unstake / withdraw from a DeFi endpoint into the Emporium contract) intending the proceeds to end up as their own shielded note. Once that signature is broadcast to be executed (e.g. sits in a relay/mempool, or is otherwise observable — signatures are not access-controlled, `verifyWallet` never checks `msg.sender`/`circomData.originalSender` against `stack.signerAddress`), any unprivileged attacker constructs their own fully valid `CircomData` + ZK proof (proving only their own trivial/zero-value UTXO spend) with the exact same `emporiumMessage`/`ops`/`maxFee`/`deadline`, but with `circomData.stealthAddressStructure` set to their own key and `circomData.erc20TokenAddresses` pointing at the token the ops actually move into Emporium. They call `Hinkal.transact` first. `verifyWallet` accepts the signature (since it never checked the token/destination fields), the ops execute and legitimately transfer funds from the signer's `HinkalWallet` into the Emporium contract, and `handleOut` mints the resulting proceeds to the attacker's chosen stealth address instead of the signer's. `usedMessages[emporiumMessage]` is then marked used, permanently preventing the rightful signer from ever redeeming their own operation (the funds are gone and the message can't be replayed).

None of the existing guards catch this: `performHinkalChecks`/`onlyAllowedRecipient` only gate which relay contract can call `runAction`, not the destination fields; the SNARK circuit binds `stealthAddressStructure` to the *submitter's* own proof, not to `stack.signerAddress`; `insertNullifiers`/`rootHashExists` protect double-spend of the attacker's own trivial input UTXOs, which are unrelated to the victim's wallet funds being moved by the ops.

### Impact Explanation
Critical — direct theft of the value that the signed wallet operation was meant to produce for the signer. The signer's wallet is debited/acted upon exactly as they authorized (so `onlyAllowedRecipient`/`verifyWallet`'s ops-signature check passes), but the resulting shielded UTXO — the actual economic proceeds — is minted to an attacker-chosen stealth address instead of the signer's. This is repeatable against every pre-signed `EmporiumStack` an attacker can observe before it is consumed, and once executed the `usedMessages` flag makes it irreversible (the rightful signer can never claim the funds via that message again).

### Likelihood Explanation
Requires only that a signed `EmporiumStack` payload exist and be visible/obtainable to an unprivileged party before it is consumed (e.g., relayed through any off-chain channel, mempool, or a keeper network — a realistic precondition for any meta-tx-style flow like this). The attacker needs no special role: they can freely craft their own `CircomData`/proof for a zero/self-value transaction and simply need to win the race to call `Hinkal.transact` first with the intercepted signature and their own destination fields. Cost is a normal gas-paying transaction; feasibility is high given `verifyWallet` never ties the signature to `msg.sender`, `circomData.originalSender`, or any of the payout-determining fields.

### Recommendation
Include `circomData.stealthAddressStructure`, `circomData.erc20TokenAddresses`, and `circomData.amountChanges` (or at minimum a commitment/hash of them) inside the EIP-712 digest verified in `verifyWallet`, so the signer explicitly authorizes both the operations to run and the exact destination/token/amount of the resulting shielded output. Alternatively, bind the payout deterministically to a signer-specified recipient stealth address stored as part of `EmporiumStack` itself, and reject any `circomData` whose stealth address/token list diverges from what was signed.

### Proof of Concept
Foundry test plan:
1. Deploy `HinkalFactory`/`Hinkal`, `EmporiumUpgradeable`, and a `HinkalWallet` for `signer` (a simulated victim EOA); allow-list Emporium as a recipient.
2. Have `signer` sign an `EmporiumStack` with `ops = [{invokeWallet:true, endpoint: mockRewardVault, callData: claim(), value:0}]`, `maxFee`, `deadline`, over `EMPORIUM_SIGNATURE_TYPEHASH`; the mock vault sends reward tokens to `signer`'s `HinkalWallet`'s balance ultimately into the Emporium contract's own balance via the call.
3. Generate a valid ZK proof for `attacker`'s own trivial UTXO set (zero-value spend) with `circomData.stealthAddressStructure = attackerStealthAddress`, `circomData.erc20TokenAddresses = [rewardToken]`, `circomData.externalActionData.externalActionMetadata = abi.encode(signerStack)` (the same signature bytes signer produced).
4. Call `Hinkal.transact` as `attacker` before `signer`/their relay does.
5. Assert: (a) `verifyWallet` does not revert (`InvalidSignature` not thrown) even though `circomData.stealthAddressStructure` differs from anything `signer` signed; (b) the emitted/minted UTXO commitment corresponds to `attackerStealthAddress`, not any address `signer` controls; (c) `$.usedMessages[emporiumMessage] == true` afterward, so `signer` can never redeem the same operation; (d) reward tokens debited from `signer`'s wallet ended up shielded to `attacker`. [6](#0-5)

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-124)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-349)
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

        if (block.timestamp > stack.deadline) {
            revert SignatureExpired();
        }

        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
    }
```

**File:** contracts/CircomDataBuilder.sol (L180-238)
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

        input[index++] = circomData.stealthAddressStructure.H0x;
        input[index++] = circomData.stealthAddressStructure.H0y;

```

**File:** contracts/external-actions/emporium/HinkalWallet.sol (L21-34)
```text
    modifier onlyEmporium() {
        if (msg.sender != emporium) {
            revert NotAllowedToCallWallet();
        }
        _;
    }

    function callHinkalWallet(
        address endpoint,
        bytes calldata data,
        uint value
    ) external onlyEmporium returns (bool success, bytes memory err) {
        (success, err) = endpoint.call{value: value}(data);
    }
```
