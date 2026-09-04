### Title
`EmporiumUpgradeable.verifyWallet` signs `EmporiumOperation[]`/fee/deadline but never binds the output `stealthAddressStructure`, letting any observer redirect the credited UTXO to themselves - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`verifyWallet` recovers a signer from `EMPORIUM_SIGNATURE_TYPEHASH`, which only commits to `(emporiumMessage, ops hash, maxFee, deadline)`. The resulting output UTXO owner (`circomData.stealthAddressStructure`, consumed in `handleOut`) is a totally separate field that is neither part of that EIP-712 hash nor constrained to the wallet owner in any other on-chain check. Anyone who obtains the valid `(v,r,s, ops, maxFee, deadline, emporiumMessage)` tuple (e.g. by observing a pending transaction before it lands) can wrap it in their own `CircomData`/proof with their own `stealthAddressStructure` and steal the value produced by executing the victim's authorized wallet operations.

### Finding Description
The claimed equality is: `(address that owns the output UTXO created in handleOut)` == `(address the signer of EmporiumOperation[] authorised to receive proceeds)`.

- `verifyWallet` builds `hashedMessage` from `EMPORIUM_SIGNATURE_TYPEHASH` over only `circomData.emporiumMessage`, `_hashEmporiumOps(stack.ops)`, `stack.maxFee`, `stack.deadline`: [1](#0-0) . Nothing about `circomData.erc20TokenAddresses`, `circomData.feeStructure`, `circomData.relay`, or `circomData.stealthAddressStructure` is included in the signed struct.
- After the ops execute, `handleOut` creates the output UTXO using `circomData.stealthAddressStructure` taken directly from the calldata that the *transaction submitter* (not the signer) supplied: [2](#0-1) .
- The Groth16 proof for the "normal" path does encode `stealthAddressStructure` as public inputs (`H1x`, `H1y`, `stealthAddress`, `H0x`, `H0y`), but these are derived purely from `spendingPublicKey`/`nullifyingPrivateKey`/`H0Ax`/`H0Ay`, which are witness values fully controlled by whoever constructs the proof — the circuit has no constraint tying them to `stack.signerAddress`: [3](#0-2)  and [4](#0-3) .
- `Hinkal.transact`'s balance/slippage checks only constrain magnitudes (`balanceDif == amountChanges[i] + utxoAmount`), never the owner field inside the UTXO struct: [5](#0-4) .
- `usedMessages[emporiumMessage]` is only checked/marked inside `verifyWallet`, at execution time, so whichever transaction lands first consumes the nonce: [6](#0-5) .

Exploit flow: an attacker observes a pending `Hinkal.transact` call (mempool) carrying a valid Emporium signature `(v,r,s)` over `ops/maxFee/deadline/emporiumMessage` that authorizes withdrawing/moving value out of the victim's `IHinkalWallet(stack.signerAddress)`. The attacker copies these signed fields verbatim into a new `EmporiumStack`, builds their own `CircomData` (own `erc20TokenAddresses`, own `stealthAddressStructure` pointing to their own spending key), generates their own valid proof for that `CircomData` (no secret belonging to the victim is required since no input UTXOs are consumed for the credit side), and submits `transact()` with higher priority. `verifyWallet` still recovers `stack.signerAddress` correctly (only unmodified fields are hashed), `stack.ops` execute exactly as authorized against the victim's wallet, and `handleOut` mints the resulting UTXO to the attacker's `stealthAddressStructure`. The victim's original transaction then reverts with `UsedMessage`.

### Impact Explanation
The attacker, an unprivileged party, steals the shielded value that results from operations the wallet owner authorized (e.g. withdrawals, swaps performed through `IHinkalWallet.callHinkalWallet`), redirecting the created output UTXO to their own stealth address. This is direct theft of shielded output value — matches the Critical category (theft of shielded funds / value never authorized to the recipient). It is repeatable against every Emporium transaction that uses a non-zero `stack.signerAddress` and produces a positive balance change, each time the signed payload becomes observable prior to inclusion.

### Likelihood Explanation
Preconditions: `stack.signerAddress != address(0)`, the Emporium operations produce a positive token balance increase (`erc20TokenAddresses.length > 0`), and the signed transaction/its fields become visible before being mined (mempool visibility, or any distribution path where the signature travels outside a single atomic transaction). Attacker cost is generating one Groth16 proof over their own chosen witness data and out-bidding the original transaction's gas — both trivially achievable for any unprivileged party. No relayer/RPC compromise or social engineering is required; observing pending on-chain transactions is a standard, permissionless capability.

### Recommendation
Bind the output recipient to the signed authorization: include `circomData.stealthAddressStructure` (and ideally the full `erc20TokenAddresses`/`feeStructure`/`relay` set) inside `EMPORIUM_SIGNATURE_TYPEHASH` so the wallet owner explicitly signs where proceeds must go, or otherwise require that `handleOut`'s destination match a signer-committed recipient (e.g., pass an authorized recipient address as an EIP-712-signed field and enforce `circomData.stealthAddressStructure.stealthAddress == authorizedRecipient`).

### Proof of Concept
Hardhat test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable`, a test `IHinkalWallet`, and a mock endpoint that returns tokens/ETH when called by the wallet.
2. Victim signs an `EmporiumStack` (`ops` = withdraw tokens from their `IHinkalWallet`, `maxFee`, `deadline`, `emporiumMessage=N`) with EIP-712 typed data matching `EMPORIUM_SIGNATURE_TYPEHASH`.
3. Build `CircomData_A` with `stealthAddressStructure_A` (victim's intended address) and generate proof A for `MainEVMCircuit` with `emporiumMessage=N`, same `ops` hash.
4. Build `CircomData_B` with identical `emporiumMessage=N`, identical decoded `EmporiumStack` (`v,r,s`, `ops`, `maxFee`, `deadline`), but `stealthAddressStructure_B` pointing to attacker's own key/spendingPublicKey; generate proof B for the same circuit with attacker's own witness (no victim secrets needed).
5. Submit `transact()` with `CircomData_B`/proof B first — assert it succeeds, `verifyWallet` passes (signature recovers to victim), `stack.ops` execute against the victim's wallet, and the created UTXO's `stealthAddressStructure` equals `stealthAddressStructure_B` (attacker's).
6. Submit `transact()` with `CircomData_A`/proof A — assert it reverts with `UsedMessage`.
7. Assert equality check: `stealthAddressStructure_B.stealthAddress != stack.signerAddress`-derived intended recipient, proving the attacker, not the signer, received the funds.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L318-337)
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
```

**File:** circuits/MainEVMCircuit.circom (L80-90)
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

```

**File:** contracts/CircomDataBuilder.sol (L180-192)
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
```

**File:** contracts/Hinkal.sol (L97-146)
```text
            for (uint64 i; i < circomData.erc20TokenAddresses.length; i++) {
                int256 balanceDif;

                if (circomData.erc20TokenAddresses[i] == address(0)) {
                    balanceDif =
                        int256(newBalances[i]) +
                        int256(msg.value) -
                        int256(oldBalances[i]);
                } else {
                    balanceDif =
                        int256(newBalances[i]) -
                        int256(oldBalances[i]);
                }
                // balance inequality to check that minimum amount of token is received/given
                require(
                    balanceDif >= circomData.slippageValues[i],
                    "slippage param is violated"
                );

                uint256 utxoAmount = 0;
                for (uint j = 0; j < utxoSet.length; j++) {
                    if (
                        utxoSet[j].erc20Address ==
                        circomData.erc20TokenAddresses[i]
                    ) {
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
