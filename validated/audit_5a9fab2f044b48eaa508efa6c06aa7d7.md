### Title
EmporiumStack EIP-712 signature never binds `stealthAddressStructure` (or any element proving submitter identity), allowing hijack of a signed wallet action to redirect the resulting UTXO to an attacker - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.verifyWallet` recovers the wallet owner's ECDSA signature over `EMPORIUM_SIGNATURE_TYPEHASH`, which commits only to `emporiumMessage`, the hash of `ops`, `maxFee`, and `deadline`. It never commits to `circomData.stealthAddressStructure` (or any other CircomData field), so once these four signed values become publicly known (e.g. by observing them in a still-pending mempool transaction), any unprivileged party can wrap them in an entirely different, self-authored `CircomData`/Groth16 proof that names their own stealth address as the destination of the resulting UTXO, and front-run the legitimate submission.

### Finding Description
Broken equality: the wallet owner signs "(assets moved by `ops`, `maxFee`, `deadline`, `emporiumMessage`)" but the actual on-chain effect is "(assets moved by `ops`) → UTXO at `circomData.stealthAddressStructure`". The signed digest and the resulting fund destination are different values, and nothing forces them to match.

Code path:
- `EmporiumUpgradeable.verifyWallet` builds the signed hash from only `circomData.emporiumMessage`, `_hashEmporiumOps(stack.ops)`, `stack.maxFee`, `stack.deadline`: [1](#0-0) 
- The only replay guard is a one-time consumption of the raw `circomData.emporiumMessage` nonce, marked used *before* the signature check even completes for the zero-signer case, and generally before `ops` execution: [2](#0-1) 
- `runAction` then executes the (immutable, signature-bound) `ops` against the wallet, measures the resulting balance change on the calling contract, and wraps it into a UTXO using `circomData.stealthAddressStructure`, which is **not** part of `verifyWallet`'s signed digest: [3](#0-2) 
- Separately, `CircomDataBuilder.getSignedMessageHash` does bind `stealthAddressStructure` (H1x, H1y, H0x, H0y) plus `calldataHash`, `emporiumMessage`, etc. into the *EdDSA* `signedMessageHash` used inside the ZK circuit: [4](#0-3) . But this EdDSA signature is produced with `spendingPublicKey`/`nullifyingPrivateKey`, which the attacker fully controls for their own proof — it authenticates only that the attacker consents to their own chosen fields, it says nothing about the wallet owner's intent.

Exploit flow:
1. Victim (wallet owner) signs an `EmporiumStack` (`v,r,s`) over `(emporiumMessage, ops, maxFee, deadline)` and submits (or has their relay submit) a `transact()` call with their own legitimate `CircomData`, including their own `stealthAddressStructure` for the resulting note.
2. Because this transaction (and its calldata, including the plaintext `emporiumMessage` and `(v,r,s)`) is publicly visible once broadcast (even unconfirmed, in the mempool), an unprivileged attacker copies `stack.v,r,s`, `stack.ops`, `stack.maxFee`, `stack.deadline`, `stack.signerAddress`, and `circomData.emporiumMessage` verbatim.
3. The attacker crafts their own `CircomData` (their own `spendingPublicKey`/`nullifyingPrivateKey`, their own `erc20TokenAddresses`/`amountChanges`/`outCommitments` consistent with the circuit's `inTotal + amountChanges === outTotal` constraint, and their own `stealthAddressStructure`), and generates their own valid Groth16 proof for `MainEVMCircuit`/`MainEVMCircuitMin` — this is fully within the attacker's control since it's their own proof over their own private inputs.
4. The attacker front-runs the victim's pending transaction with higher gas. `verifyWallet` recovers `stack.signerAddress` correctly (same `v,r,s`, same `ops`/`maxFee`/`deadline`/`emporiumMessage`), passes, marks `emporiumMessage` used, and executes the victim's pre-authorized `ops` against the victim's `HinkalWallet`, moving the victim's real funds. `handleOut` then wraps the resulting balance change into a UTXO owned by the **attacker's** `stealthAddressStructure`.
5. The victim's original transaction later reverts with `UsedMessage()`, having lost the funds moved by `ops` to the attacker's shielded note.

Existing guards fail to prevent this because:
- `verifyWallet` never checks `stealthAddressStructure`, `originalSender`, `erc20TokenAddresses`, `amountChanges`, or `outCommitments` — only `ops`/`maxFee`/`deadline`/`emporiumMessage`.
- `performHinkalChecks`'s `originalSender`/`relay` check only verifies internal consistency of the attacker's own `circomData` (attacker sets `relay = address(0)` and `originalSender = msg.sender`), it does not tie the transaction to the wallet owner in any way.
- The circuit's `sigVerifier`/`OverflowPreventer`/`ForceEqualIfEnabled` constraints only prove the attacker's proof is internally consistent for the attacker's own inputs; they cannot and do not constrain who the wallet owner intended as recipient, because the wallet owner's EIP-712 signature never included that information in the first place.

### Impact Explanation
Critical: direct theft of the assets moved by a legitimately, off-chain pre-signed `EmporiumStack` operation. The wallet owner's real, on-chain funds (via `ops` executed against their `HinkalWallet`) are redirected into a UTXO note controlled by the attacker's stealth address instead of the wallet owner's. This is repeatable against any wallet owner (or their relay) whose signed Emporium transaction is observable before confirmation.

### Likelihood Explanation
Preconditions: the attacker must observe a not-yet-mined transaction containing a full `EmporiumStack` signature plus its `ops`/`maxFee`/`deadline`/`emporiumMessage` (trivially available from any public mempool or any already-broadcast, still-pending calldata), and must be able to construct their own valid Groth16 proof (achievable for their own arbitrary spendingPublicKey/output amounts, with no ZK secrets belonging to the victim required). Cost is just gas plus proof generation; feasibility is high given `ops` and signature fields are plaintext, unencrypted calldata fields, and front-running via higher gas is standard on public mempools.

### Recommendation
Include `circomData.stealthAddressStructure` (and ideally `circomData.originalSender`/`relay`, `erc20TokenAddresses`) in the `EMPORIUM_SIGNATURE_TYPEHASH` digest that `verifyWallet` signs and recovers, so that the wallet owner explicitly authorizes both the `ops` to execute AND the destination of the resulting shielded note in the same signature.

### Proof of Concept
Hardhat test:
1. Deploy `Hinkal`, `EmporiumUpgradeable`, `HinkalWallet` for a victim signer; fund the wallet with an ERC20 token.
2. Victim signs an `EmporiumStack` (`ops` = transfer wallet balance to Emporium contract, `maxFee`, `deadline`) with a fixed `emporiumMessage`, intending `circomData.stealthAddressStructure = victimStealth`.
3. Simulate mempool visibility: attacker copies `(v,r,s, ops, maxFee, deadline, emporiumMessage)`.
4. Attacker builds their own `CircomData` with `stealthAddressStructure = attackerStealth`, generates a real snarkjs Groth16 proof for `MainEVMCircuitMin`/`MainEVMCircuit` with self-consistent private inputs.
5. Submit attacker's `transact()` before the victim's transaction is mined.
6. Assert: `verifyWallet` succeeds, `ops` executes moving the victim wallet's tokens, and the resulting inserted `outCommitments` UTXO decrypts/derives to `attackerStealth`, not `victimStealth`. Then assert the victim's original transaction reverts with `UsedMessage()`.
   - Equality check before: intended destination == `victimStealth`. Equality check after: actual destination == `attackerStealth`. They differ, confirming the vulnerability.

### Citations

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L318-335)
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
