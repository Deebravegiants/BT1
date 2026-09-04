### Title
EmporiumStack signature does not bind `circomData.stealthAddressStructure` (or recipient/token set), letting a front-runner redirect authorized wallet-operation proceeds to themselves - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EMPORIUM_SIGNATURE_TYPEHASH` only commits to `(emporiumMessage, ops, maxFee, deadline)` [1](#0-0) . It never binds `circomData.stealthAddressStructure`, the ERC20 token set, or any other `CircomData` field, even though `handleOut` uses `circomData.stealthAddressStructure` verbatim to construct the newly-created output UTXO for whatever balance the signed `ops` produced [2](#0-1) . Since the attacker generates their own proof/`CircomData` around a reused, still-valid `EmporiumStack` signature, they can redirect the resulting shielded output note to a stealth address they control.

### Finding Description
The broken equality: **stealthAddressStructure the victim/signer authorized (none — the signature scheme has no field for it)** vs. **stealthAddressStructure the on-chain-created output UTXO is credited to** (`circomData.stealthAddressStructure`, fully attacker-supplied in the calldata of the transaction that ultimately lands).

`verifyWallet` reconstructs the EIP-712 hash strictly from `circomData.emporiumMessage`, `_hashEmporiumOps(stack.ops)`, `stack.maxFee`, and `stack.deadline` [3](#0-2) . Nothing in this hash constrains which `erc20TokenAddresses`, which relay, or — critically — which `stealthAddressStructure` will receive the leftover balance produced when the signed `ops` execute via `IHinkalWallet(stack.signerAddress).callHinkalWallet(...)` (Case 1, stateful wallet interaction) [4](#0-3) .

After the ops run, any positive balance delta on Emporium's own token balances is wrapped into a fresh on-chain-created UTXO whose owner is taken directly from `circomData.stealthAddressStructure`, supplied by whoever calls `Hinkal.transact` (attacker), with no cross-check against the signer's intended recipient: [5](#0-4) . This UTXO is then inserted into the Merkle tree by `Hinkal.transact` via `insertCommitments`, using `createOnchainCommitment` built purely from that struct [6](#0-5) .

The single global nonce, `emporiumMessage` (`usedMessages[circomData.emporiumMessage]`), only prevents replay after one submission succeeds [7](#0-6) ; it does not tie the message to a specific `stealthAddressStructure` or a specific submitter. `calldataHash` in `CircomData` exists to bind a prover's own proof to their own calldata (anti-tampering by a *different* relay after generation), but since the attacker here generates their own fresh proof around their own chosen `stealthAddressStructure`, `calldataHash` self-consistently matches their own submission and provides no protection against them simply choosing a different `stealthAddressStructure` than the victim intended.

Attacker's exact call: observe a pending/stranded `Hinkal.transact` calldata (mempool or a previously broadcast but unmined tx) containing a signed `EmporiumStack{v,r,s,signerAddress,ops,maxFee,deadline}` and its `emporiumMessage`. Front-run it with their own `Hinkal.transact(a,b,c,dimensions,circomData')` where `circomData'.externalActionData.externalActionMetadata` re-encodes the identical `EmporiumStack` (same signature, same `emporiumMessage`) but `circomData'.stealthAddressStructure = attacker's key`, and `a,b,c` is a freshly (self) generated valid proof satisfying `performHinkalChecks`/`verifyProof` for the attacker's own (possibly zero-value) nullifier/commitment set. `verifyWallet` still passes because signature verification only checks `(message, ops, maxFee, deadline)` match, which are unchanged. The signed ops execute against the victim's wallet (`stack.signerAddress`) producing real value into Emporium's balance, and `handleOut` credits that value to the attacker's `stealthAddressStructure`.

### Impact Explanation
Direct theft of the shielded output UTXO representing the proceeds of a wallet operation the victim authorized only in terms of *which calls to make*, not *who receives the result*. This meets the Critical bar: direct theft of shielded/in-flight user funds via a field (`stealthAddressStructure`) the signature/proof never actually constrained relative to the authorized operation. It is repeatable for every EmporiumStack the attacker can observe and front-run before it is consumed.

### Likelihood Explanation
Preconditions: a victim (or their relay) has broadcast/prepared a `Hinkal.transact` call using the Emporium external action with `stack.signerAddress != address(0)` and ops that move real value into the Emporium contract's balance; the `emporiumMessage` nonce is not yet marked used. Attacker cost is generating one valid proof for their own trivial/zero-effect main circuit inputs (something any unprivileged depositor can produce) plus gas to front-run. This is feasible any time a signed EmporiumStack payload becomes visible before inclusion (public mempool, stranded/dropped tx, or a relay leak), and is repeatable per victim submission.

### Recommendation
Include `circomData.stealthAddressStructure` (and ideally the full `erc20TokenAddresses` array and `relay`) inside `EMPORIUM_SIGNATURE_TYPEHASH` so the signer explicitly authorizes both the operations and the destination/recipient of any resulting output, or otherwise bind `emporiumMessage` at signing time to a specific `circomData` hash (e.g., signer signs `keccak256(abi.encode(ops, maxFee, deadline, stealthAddressStructure, erc20TokenAddresses))`) so that reusing the signature under different destination fields is impossible.

### Proof of Concept
Hardhat test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable`, a mock `IHinkalWallet` representing the victim's wallet holding some ERC20 balance, and a mock endpoint the wallet calls to move that ERC20 into Emporium's balance.
2. Victim signs an `EmporiumStack` (`v,r,s`, `signerAddress = victimWallet`, one op with `invokeWallet=true` calling the mock endpoint that transfers tokens from `victimWallet` into Emporium) plus `maxFee`, `deadline`, and picks `emporiumMessage = M`. Assemble `circomDataVictim` with `stealthAddressStructure = victimStealthKey`.
3. Do NOT submit the victim's tx yet (simulate front-run window).
4. Attacker builds `circomDataAttacker` reusing the identical encoded `EmporiumStack` bytes/signature and `emporiumMessage = M`, but sets `stealthAddressStructure = attackerStealthKey`; attacker locally (snarkjs) generates a fresh, valid proof for a trivial/zero-value main circuit satisfying `performHinkalChecks`/`verifyProof`/root checks.
5. Call `Hinkal.transact` with the attacker's payload first.
6. Assert: `verifyWallet` succeeds (no revert `InvalidSignature`), the mock endpoint call executes moving victim's wallet funds into Emporium, `handleOut` creates a UTXO/commitment with `stealthAddressStructure = attackerStealthKey` (verify via emitted commitment/nullifier event or by decrypting/inspecting the on-chain commitment inserted), and `usedMessages[M] == true`.
7. Assert the victim's original tx (same `emporiumMessage = M`) now reverts with `UsedMessage`, proving the victim's intended output never lands with `victimStealthKey`, and the value is unrecoverable by the victim — confirming the equality `stealthAddressStructure signed (none) != stealthAddressStructure credited (attacker)`.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L36-39)
```text
    bytes32 private constant EMPORIUM_SIGNATURE_TYPEHASH =
        keccak256(
            "EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)EmporiumOperation(address endpoint,bool invokeWallet,uint128 value,bytes callData)"
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L97-101)
```text
            // CASE 1: Stateful Interaction
            if (op.invokeWallet && stack.signerAddress != address(0)) {
                (success, err) = IHinkalWallet(stack.signerAddress)
                    .callHinkalWallet(op.endpoint, op.callData, op.value);
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L308-312)
```text
        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;
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

**File:** contracts/Hinkal.sol (L122-132)
```text
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
```
