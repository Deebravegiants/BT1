### Title
Unauthorized `transferFrom` via attacker-controlled `originalSender` in `DepositOnChainUtxosExternalAction` - (File: `contracts/external-actions/DepositOnChainUtxosExternalAction.sol`)

### Summary
`DepositOnChainUtxosExternalAction.runAction` pulls ERC20 tokens with `transferERC20TokenFrom(tokenAddress, userAddress, msg.sender, tokenTotal)` where `userAddress = circomData.originalSender` [1](#0-0) [2](#0-1) . Although `originalSender` is folded into `calldataHash` and hence into `signedMessageHash` [3](#0-2) [4](#0-3) , the signature/proof that the circuit actually checks authenticates the key of the shielded UTXOs being spent by the *caller* — not any consent from the `originalSender` address itself. This is structurally the same flaw class as `SquidMulticall`: a contract executes `transferFrom(victim, self, amount)` where the "authorization" (the multicall shape / here the ZK proof) is valid for the caller's own action but never proves the token owner consented to this specific pull.

### Finding Description
`runAction` requires `deltaAmounts[i] == 0` for every token [5](#0-4) . This value is computed in `Hinkal._calculateDeltaAmount` purely from `circomData.onChainCreation[i]`: if `onChainCreation[i]` is `true`, the delta is forced to `0` regardless of `amountChanges[i]` [6](#0-5) . So an attacker can trivially satisfy this check by setting `onChainCreation[i] = true` for every token they want to steal.

The actual amount pulled, `tokenTotal`, comes from `utxoAmounts`, which is decoded from `circomData.externalActionData.externalActionMetadata` — an arbitrary, caller-supplied byte blob [7](#0-6) . This blob is never validated against the amounts committed in the circuit's `amountChanges` public signal; it is only used to build the on-chain UTXO leaves and to pull tokens.

Crucially, the address the tokens are pulled *from* is `circomData.originalSender`, which is fully attacker-controlled and only required to be non-zero [1](#0-0) . The ZK proof submitted to `Hinkal.transact` proves knowledge of the attacker's own spendable nullifiers/root membership and a signature over `signedMessageHash`/`calldataHash` — but that signature is produced with the key controlling the shielded UTXO(s) the *attacker* is spending, not with any key belonging to `originalSender`. Including `originalSender` inside `calldataHash` only guarantees the hash can't be tampered with in flight; it does not prove `originalSender` ever authorized this specific deposit/pull. Any Hinkal user who has approved the `Hinkal` contract to move their ERC20 tokens (the standard, expected UX for the normal `_internalTransact` deposit path, where users approve `address(this)`/Hinkal directly [8](#0-7) ) is therefore a drain target: the attacker sets `originalSender = victim` and the action calls `transferERC20TokenFrom(token, victim, msg.sender, tokenTotal)` where `msg.sender` is `Hinkal` itself (the caller of `runAction` via `_externalTransact`) [9](#0-8) .

The stolen funds land inside Hinkal's balance and are then wrapped into new UTXOs whose recipient stealth address (`circomData.stealthAddressStructure`) is also fully attacker-controlled, so the attacker becomes the owner of shielded value backed by the victim's stolen tokens. Hinkal's top-level balance-diff invariant in `transact` (`balanceDif == (onChainCreation[i] ? 0 : amountChanges[i]) + utxoAmount`) is satisfied trivially because `onChainCreation[i]=true` zeroes out the RHS term and `utxoAmount` is defined to equal the same `tokenTotal` that was pulled [10](#0-9)  — so the accounting equation Hinkal enforces never detects that the source of funds was an unauthorized third party rather than the depositor described by the proof.

### Impact Explanation
This is direct theft of a user's on-chain ERC20 allowance/funds via an unauthorized `transferFrom`, executed without any consent from the token owner (`originalSender`/victim) and backed only by the attacker's own unrelated ZK proof. The stolen value is then minted into shielded UTXOs under the attacker's control. This matches the Critical impact category: "direct theft of shielded or in-flight user funds" / "executing calls or moving assets a wallet owner or prover never authorised."

### Likelihood Explanation
Exploitability only requires: (1) a victim who has previously granted ERC20 allowance to the `Hinkal` contract (the standard deposit approval flow), and (2) the attacker owning any spendable shielded UTXO of their own to produce a valid proof/signature for their side of the transaction. No admin, relay, or victim signature is needed — the attacker fully controls `originalSender`, `onChainCreation`, `externalActionMetadata` (i.e. `utxoAmounts`), and the destination stealth address.

### Recommendation
`DepositOnChainUtxosExternalAction` must not accept `originalSender` as an unauthenticated, attacker-supplied address. The action should either (a) always pull from `circomData.originalSender == tx signer` enforced the same way `_internalTransact` enforces `externalActionData.externalAddress == msg.sender`, i.e., require the ZK proof's signer/prover to equal `originalSender`, or (b) require a fresh EIP-712/ECDSA signature from `originalSender` specifically authorizing this exact `tokenAddress`/`tokenTotal` pull, verified inside `runAction` before calling `transferERC20TokenFrom`.

### Proof of Concept
1. Victim has approved `Hinkal` for token `T` (e.g. via the standard deposit flow) with allowance ≥ `X`.
2. Attacker owns a valid, spendable shielded UTXO of their own and constructs a `transact` call with:
   - `externalActionData.externalActionId` = the registered id for `DepositOnChainUtxosExternalAction`.
   - `onChainCreation[i] = true` for token `T` (forces `deltaAmounts[i] = 0`, satisfying `_calculateDeltaAmount`/`runAction`'s check).
   - `originalSender = victim`.
   - `externalActionData.externalActionMetadata` = `abi.encode(uint256[][])` describing `utxoAmounts[T-index] = [X]` (i.e., `tokenTotal = X`).
   - `stealthAddressStructure` = attacker's own address/keys.
   - A valid proof/signature over the attacker's own nullifiers/root (unrelated to `victim`).
3. `Hinkal.transact` verifies the proof (valid, since it only proves attacker's own UTXO ownership), calls `_externalTransact` → `DepositOnChainUtxosExternalAction.runAction`.
4. `runAction` executes `transferERC20TokenFrom(T, victim, Hinkal, X)`, draining `X` of token `T` from the victim using their pre-existing allowance, and creates a new UTXO of amount `X` for the attacker's stealth address [11](#0-10) .
5. Hinkal's balance-diff check passes because `onChainCreation[i]=true` zeroes the expected non-UTXO delta and `utxoAmount == X == balanceDif` [10](#0-9) , so the transaction completes and the attacker walks away with `X` of the victim's tokens as shielded balance.

### Citations

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L31-35)
```text
        address userAddress = circomData.originalSender;
        require(
            userAddress != address(0),
            "DepositOnChainUtxosExternalAction: Invalid originalSender"
        );
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L37-44)
```text
        uint256[][] memory utxoAmounts = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (uint256[][])
        );
        require(
            utxoAmounts.length == tokenCount,
            "DepositOnChainUtxosExternalAction: metadata length mismatch"
        );
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L49-53)
```text
        for (uint256 i = 0; i < tokenCount; i++) {
            require(
                deltaAmounts[i] == 0,
                "DepositOnChainUtxosExternalAction: Delta amount must be zero"
            );
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L66-82)
```text
                utxoSet[utxoIndex] = UTXO({
                    amount: amount,
                    erc20Address: tokenAddress,
                    stealthAddressStructure: circomData.stealthAddressStructure,
                    timeStamp: circomData.timeStamp + utxoIndex
                });
                utxoIndex++;
            }

            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
            }
```

**File:** contracts/CircomDataBuilder.sol (L37-54)
```text
    function getHashedCalldata2(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.hookData,
                        circomData.encryptedOutputs,
                        circomData.onChainEncryptedOutput,
                        circomData.feeStructure,
                        circomData.onChainCreation,
                        circomData.originalSender,
                        circomData.extraData
                    )
                )
            );
    }
```

**File:** contracts/CircomDataBuilder.sol (L97-132)
```text
    function getSignedMessageHash(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData,
        uint256 emporiumMessage
    ) internal pure returns (uint256) {
        // split into two encode calls to avoid "stack too deep"
        uint256 hash1 = uint256(
            keccak256(
                abi.encode(
                    chainId,
                    verifyingContract,
                    circomData.rootHashHinkal,
                    _encodeTokenAddresses(circomData.erc20TokenAddresses),
                    _encodeAmountChanges(circomData.amountChanges),
                    circomData.timeStamp,
                    _flatUint256Matrix(circomData.inputNullifiers),
                    _flatUint256Matrix(circomData.outCommitments),
                    circomData.calldataHash,
                    emporiumMessage
                )
            )
        );
        uint256 hash2 = uint256(
            keccak256(
                abi.encode(
                    circomData.stealthAddressStructure.H1x,
                    circomData.stealthAddressStructure.H1y,
                    circomData.stealthAddressStructure.H0x,
                    circomData.stealthAddressStructure.H0y
                )
            )
        );
        return
            uint256(keccak256(abi.encode(hash1, hash2))) % CIRCOM_P;
    }
```

**File:** contracts/Hinkal.sol (L134-146)
```text
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
```

**File:** contracts/Hinkal.sol (L176-187)
```text

            if (deltaAmountChange > 0) {
                require(
                    circomData.externalActionData.externalAddress == msg.sender,
                    "Deposit should come from the sender"
                );
                transferERC20TokenFromOrCheckETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    address(this),
                    uint256(circomData.amountChanges[i])
                );
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

**File:** contracts/Hinkal.sol (L383-390)
```text
    function _calculateDeltaAmount(
        CircomData calldata circomData,
        uint256 index
    ) private pure returns (int256) {
        return
            circomData.onChainCreation[index]
                ? int256(0)
                : circomData.amountChanges[index];
```
