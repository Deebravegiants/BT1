### Title
Emporium output UTXO/proceeds bound only to transactor's `circomData.stealthAddressStructure`, never to the signing wallet owner - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.verifyWallet` authenticates only `emporiumMessage`, `ops`, `maxFee`, and `deadline` via `EMPORIUM_SIGNATURE_TYPEHASH` [1](#0-0) , and `runAction`/`handleOut` credits any resulting balance increase to `circomData.stealthAddressStructure`, which is a field of the **caller's own** `CircomData`/proof supplied to `Hinkal.transact`, not anything the wallet owner signed [2](#0-1) . Any unprivileged EOA can therefore submit `Hinkal.transact` embedding a victim's previously signed, unused `EmporiumStack` in `externalActionMetadata`, together with the attacker's own proof/`stealthAddressStructure`, and receive the resulting shielded output UTXO for the assets that moved out of the victim's wallet.

### Finding Description
Equality claimed to hold: **(assets that leave the signer's wallet, and the destination of the resulting Emporium output UTXO) == (the `ops`/`maxFee` the wallet owner cryptographically signed)**.

Tracing the code shows this equality is broken:

1. `EmporiumUpgradeable.verifyWallet` recovers the signer from `EMPORIUM_SIGNATURE_TYPEHASH = "EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)EmporiumOperation(...)"` [3](#0-2) . This signature contains only `emporiumMessage`, the operations to run, `maxFee`, and `deadline` — nothing about who is allowed to submit the call or where any resulting output should go.
2. `runAction` executes `stack.ops` through the signer's `HinkalWallet` (`callHinkalWallet`, gated only by `onlyEmporium`, i.e. `msg.sender == emporium`) [4](#0-3) , moving the signer's tokens (e.g. approve + router call).
3. After the ops run, `handleOut` computes the Emporium contract's balance delta and mints an off-chain `UTXO` whose `stealthAddressStructure` and `erc20Address`/`amount` come from **`circomData.stealthAddressStructure`** — the `CircomData` struct supplied by whoever called `Hinkal.transact` in the current call, not from `stack` (the victim's signed struct) [2](#0-1) .
4. `Hinkal.transact` is callable by any address; `performHinkalChecks` only requires `circomData.originalSender == msg.sender` (or `address(0)` with a relay) and validates the proof/dimensions/calldata hash of the **caller's own** `CircomData` — it never checks any relationship between `msg.sender`/`originalSender` and `stack.signerAddress` inside the embedded `EmporiumStack` [5](#0-4) . The circuit-side `getSignedMessageHash`/`formBasicInput` binds the proof to the caller's own `stealthAddressStructure`, `outCommitments`, etc., but this is the caller's data, and nothing forces `stack.signerAddress` (the victim who signed the EmporiumStack) to equal the transactor.
5. Consequently the balance change produced by executing the victim's ops (e.g. swap proceeds) is captured entirely under the **attacker's** `outCommitments`/`stealthAddressStructure`/proof — the resulting shielded UTXO is provably spendable only by the attacker's nullifying key, never the victim's, even though the victim's wallet assets were the ones moved.

None of the existing guards prevent this: `usedMessages`/`verifyWallet` only stop *replay* of the same `emporiumMessage`, not *front-running the first, legitimate use* by a non-owner; `onlyAllowedRecipient`/`onlyEmporium` only gate which contract can call, not who benefits; `dimensionsCheck`, `checkOnchainCreation`, `rootHashExists`, and the circuit's `inTotal + amountChanges === outTotal` constraints only enforce internal consistency of the **caller's own** proof — they say nothing about whose signature authorized which recipient of the swap proceeds.

### Impact Explanation
This is a Critical direct theft of in-flight user funds: the wallet owner's assets are moved by a validly-signed `EmporiumStack` (approve + swap through a router), but the resulting shielded output UTXO/proceeds are credited to an unrelated, unprivileged third party who merely observed/obtained the signed-but-unexecuted `EmporiumStack` (e.g. via a shared relay/mempool/off-chain distribution channel) and raced to submit `Hinkal.transact` first with their own proof. This is repeatable against any EOA that delegates to `HinkalWallet` via EIP-7702 and signs an `EmporiumStack` intended to be relayed by a third party, since nothing in the signed payload restricts who may submit it or who receives the output.

### Likelihood Explanation
Preconditions: a victim EOA delegates to `HinkalWallet(emporium)` and signs an `EmporiumStack` (ops + maxFee + deadline + emporiumMessage) intending a third party (a relay) to submit it via `Hinkal.transact`. This is the intended usage pattern for gasless/relayed Emporium operations, so the precondition is not exotic — it is the designed flow. Any party capable of observing the signed payload before the intended relay submits it (or acting as an unauthorized "relay" itself, since `circomData.relay == address(0)` path only requires `originalSender == sender`, not any relationship to `stack.signerAddress`) can win the race. Attacker cost is a single proof generation for their own inputs/outputs — no special privilege needed.

### Recommendation
Bind the destination of the Emporium-produced output UTXO to the wallet owner's own signature, not to the transactor's `CircomData`. For example, include a commitment to the intended recipient (e.g. a hash of the expected `stealthAddressStructure`/output details, or restrict `msg.sender`/`originalSender` to equal `stack.signerAddress` unless the signer explicitly authorizes a different recipient) inside `EMPORIUM_SIGNATURE_TYPEHASH`, and enforce in `verifyWallet`/`runAction` that the caller's `circomData.stealthAddressStructure` (or an authorized delegate) matches what the signer actually authorized to receive proceeds.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable`, `HinkalWallet(emporium)`, a mock ERC20 and mock router.
2. `victim` EOA is configured (in test, via `vm.etch`/EIP-7702-style delegation simulation) so calls to it delegate to `HinkalWallet`; victim holds ERC20 balance.
3. Victim signs an `EmporiumStack` with `ops = [approve(router, amount) via wallet, router.swap(...) stateless]`, `maxFee`, `deadline`, `emporiumMessage = M`.
4. `attacker` (different EOA) builds their own valid ZK proof/`CircomData` with `externalActionData.externalActionMetadata = abi.encode(stack)`, `circomData.stealthAddressStructure = attackerStealthAddress`, `circomData.originalSender = attacker`.
5. Attacker calls `Hinkal.transact(...)` directly (no relay), which passes `performHinkalChecks`, then `_externalTransact` → `EmporiumUpgradeable.runAction` executes victim's signed ops, swaps victim's tokens, and `handleOut` creates the output UTXO tagged with `attackerStealthAddress`.
6. Assert: (a) victim's ERC20 balance decreased by `amount`; (b) the emitted commitment/UTXO for the swap output is decryptable/spendable only using `attacker`'s nullifying private key, not `victim`'s; (c) `usedMessages[M] == true` so the victim can never later have the same ops executed for their own benefit — the swap proceeds are irrecoverably attacker-owned.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L36-39)
```text
    bytes32 private constant EMPORIUM_SIGNATURE_TYPEHASH =
        keccak256(
            "EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)EmporiumOperation(address endpoint,bool invokeWallet,uint128 value,bytes callData)"
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-340)
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

**File:** contracts/HinkalHelper.sol (L208-236)
```text
    function performHinkalChecks(
        CircomData calldata circomData,
        Dimensions calldata dimensions,
        address sender
    ) external view returns (uint256[] memory) {
        require(
            (circomData.originalSender == address(0) &&
                circomData.relay != address(0)) ||
                (circomData.originalSender == sender &&
                    circomData.relay == address(0)),
            "invalid value for originalSender"
        );

        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
        relayerIsValid(circomData.relay);
        dimensionsCheck(circomData, dimensions);
        checkOnchainCreation(circomData);

        return
            CircomDataBuilder.formInputForCircom(
                block.chainid,
                hinkalAddress,
                circomData
            );
    }
```
