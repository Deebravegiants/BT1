### Title
Emporium withdrawal output can be redirected to an attacker-chosen stealth address by front-running a signed `ops` payload - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EMPORIUM_SIGNATURE_TYPEHASH` binds a wallet owner's EIP-712 signature only to `message`, `ops`, `maxFee`, and `deadline` [1](#0-0) . `handleOut` builds the resulting shielded `UTXO` using `circomData.stealthAddressStructure`, a field the signer never commits to [2](#0-1) . Any unprivileged party who observes a pending, validly signed `ops`/`emporiumMessage` payload can front-run it with their own `Hinkal.transact` call, supplying identical `ops`/signature but their own `stealthAddressStructure`, and capture the shielded value produced by executing those ops.

### Finding Description
The equality that should hold is: **destination of the newly-minted Emporium output UTXO == destination the `ops` signer (`stack.signerAddress`) authorized**. It is broken because `verifyWallet` only recomputes and checks a hash over `circomData.emporiumMessage`, `_hashEmporiumOps(stack.ops)`, `stack.maxFee`, and `stack.deadline` [3](#0-2) , while `handleOut` assigns the output UTXO to `circomData.stealthAddressStructure`, a caller-supplied field that never appears in `EMPORIUM_SIGNATURE_TYPEHASH` [4](#0-3) .

Path: an attacker observes/obtains a not-yet-mined, validly signed `(emporiumMessage, ops, maxFee, deadline, v, r, s)` tuple (e.g., in the mempool). They then call `Hinkal.transact` themselves with a self-crafted `CircomData` that reuses this exact `stack` (so `verifyWallet`'s ECDSA check passes against the unmodified `signerAddress`), but sets `circomData.stealthAddressStructure` to their own key material and `circomData.amountChanges`/`inputNullifiers`/`outCommitments`/`rootHashHinkal` self-consistently (with `dimensions.nullifierAmount = 0`, i.e., no shielded input spend is required at all). Because `getSignedMessageHash` and the circuit's public-input hash (`formBasicInput`) are computed purely from the attacker's own `CircomData` fields [5](#0-4) , the attacker can generate a self-consistent ZK proof without knowing any of the victim's secrets - nothing in `getSignedMessageHash` or the ZK proof cryptographically ties the output note back to `stack.signerAddress`.

Once inside `runAction`, `verifyWallet` marks `usedMessages[circomData.emporiumMessage] = true` unconditionally (even before the signature check) [6](#0-5) , so whichever transaction (attacker's or the victim's) lands first consumes the nonce - the attacker only needs to win the front-run race. The `ops` then execute exactly as signed (returning the Emporium balance), `handleOut` measures the real balance increase via `balancesAfter - balancesBefore` [7](#0-6) , and mints the resulting UTXO to the attacker's chosen `stealthAddressStructure` instead of the intended one [8](#0-7) .

None of the existing guards prevent this: `dimensionsCheck` only checks array-length consistency, permitting `nullifierAmount = 0` [9](#0-8) ; `Hinkal.sol`'s balance-diff `require` only checks that declared `amountChanges`/`utxoAmount` matches the real balance delta, not who is entitled to it [10](#0-9) ; and `onlyAllowedRecipient` only restricts which contract may invoke `runAction` (i.e., `Hinkal.sol` itself), not who may call `Hinkal.transact` [11](#0-10) .

### Impact Explanation
An attacker can steal the shielded value that results from executing a signed Emporium `ops` batch (e.g., a withdrawal returning previously-deposited funds from a DeFi protocol back into the Emporium contract) by redirecting the newly created shielded output note to their own stealth address, while the legitimate owner's `emporiumMessage` nonce gets consumed and their intended transaction reverts with `UsedMessage()`. This is direct theft of in-flight/realized user funds and is repeatable against any observable signed Emporium withdrawal, matching the Critical severity category.

### Likelihood Explanation
Preconditions: a legitimate wallet owner must have a signed `ops`/`emporiumMessage` package pending (visible in mempool or otherwise obtainable) that will realize a positive ERC20/ETH balance change in the Emporium contract. Attacker cost is only gas plus generating their own trivial (zero-nullifier) proof for a self-consistent `CircomData`; no victim secret key material is required. This is a standard front-running scenario and is repeatable for every such pending Emporium withdrawal transaction the attacker can observe.

### Recommendation
Include `circomData.stealthAddressStructure` (and ideally `erc20TokenAddresses`/expected output amounts) inside the EIP-712 struct hashed under `EMPORIUM_SIGNATURE_TYPEHASH`, so the signer explicitly authorizes the destination of the resulting output UTXO, not just the `ops` to execute. Alternatively, bind the output destination to `stack.signerAddress` directly when `signerAddress != address(0)`.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, register it as `externalActionMap[HINKAL_EMPORIUM_ACTION_ID]` and as an allowed recipient.
2. Fund victim's stealth wallet flow such that Emporium ops (e.g., a mock endpoint call) will return `X` tokens to the Emporium contract balance.
3. Have victim (`signerAddress`) sign a valid `EmporiumSignature(message, ops, maxFee, deadline)` over EIP-712.
4. Craft `circomData_A` with `stealthAddressStructure = victimStealth` and a valid trivial (0-nullifier) proof; craft `circomData_B` identical except `stealthAddressStructure = attackerStealth`, reusing the same `emporiumMessage`/`ops`/`v,r,s`.
5. Call `Hinkal.transact` with `circomData_B` first (simulating front-run): assert it succeeds, `usedMessages[message] == true`, and the resulting UTXO/commitment corresponds to `attackerStealth`.
6. Call `Hinkal.transact` with `circomData_A` (the victim's intended transaction): assert it reverts with `UsedMessage()`.
7. Assert equality broken: `outUtxo.stealthAddressStructure (attackerStealth) != signer-approved destination (victimStealth)`, for the identical `ops`/signature.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L36-39)
```text
    bytes32 private constant EMPORIUM_SIGNATURE_TYPEHASH =
        keccak256(
            "EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)EmporiumOperation(address endpoint,bool invokeWallet,uint128 value,bytes callData)"
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-146)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L306-316)
```text
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

**File:** contracts/HinkalHelper.sol (L64-104)
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

        uint previousNullifierAmount = circomData.inputNullifiers.length > 0
            ? circomData.inputNullifiers[0].length
            : 0;
        for (uint i = 1; i < circomData.inputNullifiers.length; i++) {
            require(
                circomData.inputNullifiers[i].length == previousNullifierAmount,
                "Nullifier amount should be equal"
            );
        }
        require(
            previousNullifierAmount == dimensions.nullifierAmount,
            "Actual and Claimed Nullifier Amount should be equal"
        );
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

**File:** contracts/external-actions/ExternalActionBaseUpgradeable.sol (L39-46)
```text
    modifier onlyAllowedRecipient() {
        ExternalActionBaseStorage storage $ = _getExternalActionBaseStorage();
        require(
            $._isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }
```
