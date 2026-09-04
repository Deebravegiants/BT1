### Title
Emporium wallet-signature does not bind the shielded UTXO recipient, allowing theft of wallet funds - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.verifyWallet` authorizes a stateful wallet interaction (`stack.signerAddress`'s `HinkalWallet`) via an EIP-712 signature that only commits to the operation list, `maxFee`, and `deadline`. The shielded UTXO that receives any resulting balance pulled out of the wallet is built from `circomData.stealthAddressStructure`, a field that is neither part of `EMPORIUM_SIGNATURE_TYPEHASH` nor covered by `getHashedCalldata()`. Whoever submits the `transact()` call therefore controls who receives the wallet owner's funds, not the wallet owner.

### Finding Description
`runAction` in `EmporiumUpgradeable.sol` executes `stack.ops` against the signer's `HinkalWallet` (via `IHinkalWallet.callHinkalWallet`) when `op.invokeWallet && stack.signerAddress != address(0)`, after `verifyWallet` checks a signature over `EMPORIUM_SIGNATURE_TYPEHASH`: [1](#0-0) 

This signed payload only includes `circomData.emporiumMessage`, `_hashEmporiumOps(stack.ops)`, `stack.maxFee`, and `stack.deadline`: [2](#0-1) 

After the ops run, any positive balance change on the Emporium contract is converted into a shielded UTXO in `handleOut`, whose owner is `circomData.stealthAddressStructure` — taken straight from the `CircomData` calldata argument supplied by the transaction submitter, not from the signed `stack`: [3](#0-2) 

Separately, the integrity check `performHinkalChecks` only verifies `CircomDataBuilder.getHashedCalldata(circomData) == circomData.calldataHash`, and `getHashedCalldata1`/`getHashedCalldata2` never include `stealthAddressStructure`: [4](#0-3) [5](#0-4) 

The `stealthAddressStructure` is a genuine circuit public input (bound into `inputForCircom`/the Groth16 proof), so it is fixed by whoever *generates the proof* for the `transact()` call — i.e., the transaction submitter/relayer — and is completely independent of the EIP-712 signature that the wallet owner produced to authorize the underlying `callHinkalWallet` operations. The wallet owner signs "run these exact ops, at this fee cap" but never signs "and send whatever balance results to this shielded address." This is directly analogous to the referenced Yeti Finance finding: a `_rewardOwner`/beneficiary field that is decoupled from the entity whose action/authorization actually produced the value, letting a third party redirect proceeds that rightfully belong to the authorizing party.

### Impact Explanation
Once a wallet owner signs an `EmporiumOperation[]` stack that results in a net-positive balance for the Emporium contract (e.g., withdrawing from a lending/staking position, claiming rewards, unwrapping an asset back to a spendable token via the wallet), any party holding that signature (a malicious relayer, or anyone the signature is disclosed to for meta-tx relaying) can submit the `transact()` call themselves with an attacker-chosen `stealthAddressStructure`. The resulting shielded UTXO — representing real value pulled out of the signer's on-chain `HinkalWallet` — is minted to the attacker's own shielded balance instead of the signer's. This is unauthorized theft of the wallet owner's asset, moved without their consent as to final recipient, satisfying the "Critical – direct theft of shielded/in-flight user funds" bar.

### Likelihood Explanation
Any flow that relies on a party other than the wallet owner submitting the transaction on their behalf (which is the entire purpose of the relay/meta-tx design here, since `stack.signerAddress != address(0)` is precisely the case built for delegated execution) is exposed. The signature does not need to be leaked maliciously — a cooperating relay that is supposed to merely submit the transaction on the signer's behalf can simply swap the `stealthAddressStructure` before submission, since nothing in the signed payload or the calldata-hash integrity check constrains it.

### Recommendation
Include `circomData.stealthAddressStructure` (and ideally the full output-UTXO-determining context, e.g. `erc20TokenAddresses`, `deltaAmountChanges`/expected balance changes) inside `EMPORIUM_SIGNATURE_TYPEHASH` so the wallet owner explicitly authorizes both the operations and the destination of resulting funds. Alternatively, add `stealthAddressStructure` to the fields hashed in `CircomDataBuilder.getHashedCalldata1/2` and require that hash to also be part of what `stack.signerAddress` signs.

### Proof of Concept
1. Wallet owner `Alice` deploys a `HinkalWallet` and wants to unstake/withdraw an asset via `Emporium`, netting e.g. 100 tokens back to the Emporium contract balance.
2. Alice signs an `EmporiumSignature` over `EMPORIUM_SIGNATURE_TYPEHASH` covering `emporiumMessage`, the op-hash for the unstake call, `maxFee`, `deadline` — and hands this signature (plus the ops) to a relay `Bob` to submit on-chain (standard delegated flow since `stack.signerAddress != address(0)`).
3. `Bob`, instead of using Alice's intended `stealthAddressStructure`, builds his own `CircomData`/proof with the same signed `stack` but sets `circomData.stealthAddressStructure` to his own stealth address.
4. `Bob` calls `Hinkal.transact()` → `EmporiumUpgradeable.runAction()`. `verifyWallet` succeeds (the signature only covers ops/fee/deadline, which are unchanged). The unstake executes through `Alice`'s wallet, Emporium's balance increases by 100 tokens, and `handleOut` mints a UTXO of 100 tokens to `Bob`'s `stealthAddressStructure`.
5. Alice's 100 tokens are now shielded under Bob's control; Alice receives nothing, with no way to detect or prevent this since her signature never referenced the output recipient.

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

**File:** contracts/CircomDataBuilder.sol (L20-54)
```text
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
