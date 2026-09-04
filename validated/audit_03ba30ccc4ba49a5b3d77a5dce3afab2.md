### Title
Wallet-owner EIP-712 signature never binds the destination `stealthAddressStructure` of Emporium output UTXOs, allowing any submitter of a legitimately-signed `EmporiumStack` to redirect wallet-sourced funds to their own shielded address - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.verifyWallet` only authenticates `emporiumMessage`, the hash of `ops`, `maxFee`, and `deadline` [1](#0-0) , while `handleOut` mints the resulting output UTXO to `circomData.stealthAddressStructure`, a field that is entirely chosen by whoever builds the ZK proof/circomData for the call, not by the wallet owner who signed the `EmporiumStack` [2](#0-1) . Because the SNARK circuit disables the input-ownership constraint whenever `inAmounts[i][j]==0` (the case for wallet-sourced funds entering the pool with no real input UTXO being spent), any prover can freely choose `spendingPublicKey`/`nullifyingPrivateKey`/`H0Ax,H0Ay` and thus the resulting `outStealthAddress`, meaning no cryptographic tie exists between the wallet owner's authorization and the destination of the newly minted shielded value.

### Finding Description
The equality that should hold is: **destination of the shielded UTXO created from wallet-sourced funds == destination the wallet owner authorized when signing the `EmporiumStack`**. Tracing the code shows this equality is never enforced.

- The wallet owner's EIP-712 signature covers only `EMPORIUM_SIGNATURE_TYPEHASH = EmporiumSignature(message, ops, maxFee, deadline)` [3](#0-2) , verified in `verifyWallet` [4](#0-3) . Neither `stealthAddressStructure`, `erc20TokenAddresses`, nor `amountChanges` are part of the signed payload.
- `runAction` executes the signed `ops` (which fully determine external calls made with wallet funds), then measures the Emporium contract's own balance delta and calls `handleOut` per token [5](#0-4) .
- `handleOut` physically transfers the positive balance change to `msg.sender` (the calling Hinkal contract instance, per `onlyAllowedRecipient`), and creates the logical UTXO record pointing at `circomData.stealthAddressStructure` [6](#0-5) . This field is supplied entirely by whoever assembled `circomData`/the proof for this call - i.e., the transaction submitter/prover, not the wallet owner.
- The circuit-level binding of `stealthAddressStructure` is purely self-consistency for the prover: `getSignedMessageHash` folds `stealthAddressStructure.{H1x,H1y,H0x,H0y}` into a hash that is checked via an EdDSA signature against the prover's own freely-chosen `spendingPublicKey` [7](#0-6) , [8](#0-7) . This does not authenticate the wallet owner in any way.
- Critically, for the case where wallet funds enter the pool (`amountChanges[i] > 0`, no real input UTXO spent, i.e. `inAmounts[i][j] == 0`), the only constraint tying an input UTXO's owner-key material to a real note, `ForceEqualIfEnabled` against `rootHashHinkal`, is disabled via `enabled <== inAmounts[i][j]` [9](#0-8) . This means the prover can supply arbitrary `nullifyingPrivateKey`/`spendingPublicKey`/`H0Ax,H0Ay`, and hence choose `outStealthAddress` completely freely - which is by design for creating *new* outputs to arbitrary recipients, but is problematic here because there is no other mechanism binding this "recipient" to the wallet owner who authorized the underlying fund movement.
- Attacker call sequence: obtain a wallet owner's validly signed `EmporiumStack` (ops + `v,r,s` over `message/ops/maxFee/deadline`) intended for relay/submission, then call `Hinkal.transact()` (any unprivileged submitter is permitted - `transact()` has no caller allowlist) with a freshly built `CircomData` that reuses that `stack` but substitutes the attacker's own `circomData.stealthAddressStructure`, self-chosen prover keys, and a locally generated valid proof. `verifyWallet` accepts it because the ops/fee/deadline/message hash matches the owner's signature; `handleOut` mints the resulting UTXO to the attacker's stealth address instead of the owner's.
- None of the existing guards catch this: `onlyAllowedRecipient` only checks that the caller of `runAction` is Hinkal.sol itself, not who submitted the outer `transact()`; `verifyWallet` checks ops/fee/deadline only; `insertNullifiers`/root checks are bypassed via the `inAmounts==0` disable path; and `dimensionsCheck`/`performHinkalChecks` (in `HinkalHelper`) validate array-shape/type-count invariants, not stealth-address authorization.

### Impact Explanation
Any party who obtains a wallet owner's signed `EmporiumStack` (which, by the design of this meta-tx-style flow, is meant to be submitted by an arbitrary, non-privileged relay/caller) can redirect the shielded value resulting from that wallet's authorized operation to a stealth address they control. This is direct theft of wallet-sourced funds that were legitimately pulled from the user's `HinkalWallet` via the signed `ops`, matching the Critical category ("direct theft of shielded or in-flight user funds"). The attack is repeatable for every distinct `EmporiumStack` signature the attacker can obtain, and each occurrence yields a full loss of that operation's resulting shielded balance to the attacker.

### Likelihood Explanation
Preconditions: the attacker must possess a validly-signed `EmporiumStack` (ops, `v,r,s`, `maxFee`, `deadline`) whose execution results in a positive Emporium-contract balance change for some token (e.g., wallet funds moved into Emporium via the ops, or swap proceeds landing there) — this is intrinsic to how the ops+signature scheme is meant to be relayed by untrusted third parties, per the presence of `maxFee`/`relay` fee-protection fields that anticipate an untrusted submitter. The attacker needs no victim private key and no privileged role; they only need to construct their own valid Circom proof (self-consistent, since `inAmounts==0` disables the real note-ownership check) and call `Hinkal.transact()`, which has no caller allowlist. This is entirely feasible with the tools available to an unprivileged, technically capable actor.

### Recommendation
Bind the recipient of the Emporium output UTXO(s) to the wallet owner's authorization. Concretely, include `circomData.stealthAddressStructure` (and ideally `erc20TokenAddresses`/expected `amountChanges` or a commitment to them) inside the `EMPORIUM_SIGNATURE_TYPEHASH` that the wallet owner signs via `_hashTypedDataV4` in `verifyWallet`, so that only an `EmporiumStack` whose signature also covers the intended destination can be used to mint the corresponding output UTXO. Alternatively, require `stack.signerAddress`'s own registered stealth-address commitment to be used for any UTXO derived from `balanceChange` attributable to wallet-sourced funds, rejecting circomData whose stealth address wasn't explicitly authorized by the same signature.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, a `HinkalWallet` for a `victim` EOA, `Hinkal`, and a mock ERC20/verifier that accepts locally generated Groth16 proofs (or a mock `IVerifierEVM` that returns true, isolated from the out-of-scope verifier files, to test only the contract-level logic).
2. `victim` signs an `EmporiumStack` (`ops` = `[transferFrom(victimWallet -> emporium, 1000 tokens)]` via `callHinkalWallet`, `maxFee=0`, `deadline=future`) producing `(v,r,s)` over `EMPORIUM_SIGNATURE_TYPEHASH`.
3. `attacker` (not `victim`) builds `CircomData` with `externalActionData.externalActionMetadata = abi.encode(stack)` (reusing victim's signed stack), `erc20TokenAddresses=[token]`, `amountChanges=[1000]`, `inputNullifiers` set with `inAmounts=0` (dummy/self-chosen nullifier from attacker's own arbitrary `nullifyingPrivateKey`), `outCommitments` computed from attacker's own `spendingPublicKey`, and `stealthAddressStructure` derived from attacker's own keys (not victim's).
4. Attacker generates a locally valid proof for this circomData (satisfying `inTotal(0) + amountChanges(1000) === outTotal(1000)` and the disabled `ForceEqualIfEnabled` since `inAmounts=0`), then calls `Hinkal.transact()`.
5. Assert: `verifyWallet` succeeds (equality #1 - signed ops/fee/deadline hash matches `victim`'s signature); `handleOut` mints a UTXO with `stealthAddressStructure == attacker's`, not `victim's` (equality #2 - the two `stealthAddressStructure` values diverge, proving the destination equality is broken).
6. Attacker later constructs a spend proof for the minted commitment using their own `nullifyingPrivateKey`/`spendingPublicKey` and successfully withdraws the 1000 tokens via `Hinkal.transact()`, confirming full custody/theft of funds that originated from `victim`'s wallet.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L36-39)
```text
    bytes32 private constant EMPORIUM_SIGNATURE_TYPEHASH =
        keccak256(
            "EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)EmporiumOperation(address endpoint,bool invokeWallet,uint128 value,bytes callData)"
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-151)
```text
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

**File:** circuits/MainEVMCircuit.circom (L80-98)
```text
  component stealthAddressCalculator = StealthAddressCalculator();
  stealthAddressCalculator.H0Ax <== H0Ax;
  stealthAddressCalculator.H0Ay <== H0Ay;
  stealthAddressCalculator.spendingPublicKey <== spendingPublicKey;
  stealthAddressCalculator.nullifyingPrivateKey <== nullifyingPrivateKey;
  stealthAddressCalculator.nullifyingPrivateKeyBits <== nullifyingPrivateKeyBits.out;

  outH1Ax <== stealthAddressCalculator.H1Ax;
  outH1Ay <== stealthAddressCalculator.H1Ay;
  outStealthAddress <== stealthAddressCalculator.out;

  // verifying signature
  component sigVerifier = SignatureVerifier();
  sigVerifier.spendingPublicKey <== spendingPublicKey;
  sigVerifier.eddsaSignature <== eddsaSignature;
  sigVerifier.signedMessageHash <== signedMessageHash;

  // pinning message to seed
  message <== Poseidon(1)([messageSeed]);
```

**File:** circuits/MainEVMCircuit.circom (L144-150)
```text
        // 5) Checking that transaction root hash is legit
        calcEqual[i][j] = ForceEqualIfEnabled();
        calcEqual[i][j].in[0] <== calcTransactionRootHash[i][j].rootHash;
        calcEqual[i][j].in[1] <== rootHashHinkal;
        calcEqual[i][j].enabled <== inAmounts[i][j];
        inTotal += inAmounts[i][j];
      }
```
