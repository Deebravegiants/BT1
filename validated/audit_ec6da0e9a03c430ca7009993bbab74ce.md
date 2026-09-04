### Title
Emporium zero-token action path accepts a trivially-forgeable ZK proof, letting any unprivileged EOA execute arbitrary calls from the Emporium contract with no balance-equality enforcement - (File: `circuits/MainEVMCircuitMin.circom`, `contracts/CircomDataBuilder.sol`, `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
Just as the Monero deeplink path skipped the canonical parser and let an unvalidated field (`tx_amount=(all)`) trigger a privileged control flow, Hinkal's "Emporium min" code path skips the canonical `MainEVMCircuit` signature/nullifier/root checks entirely. When `externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin`, whose corresponding circuit (`MainEVMCircuitMin`) verifies nothing about the caller's identity. Combined with `EmporiumUpgradeable.runAction`'s unauthenticated "Stateless Interaction" branch, this lets any unprivileged EOA execute arbitrary calls directly from the Emporium contract's context.

### Finding Description
`formInputForCircom` selects the minimal path whenever the action is an Emporium action with zero tracked tokens: [1](#0-0) 

The corresponding circuit template contains **no** `SignatureVerifier`, **no** `NullifierCalculator`, and **no** `MerkleRootCalculator` — it only recomputes `message = Poseidon(messageSeed)`: [2](#0-1) 

Compare this to the canonical `MainEVMCircuit`, which enforces EdDSA signature validity, nullifier correctness, and Merkle-root membership as hard constraints before any action is trusted: [3](#0-2) 

Because `messageSeed` is a private witness fully chosen by the prover, and `circomData.emporiumMessage` is a value the transaction submitter also freely chooses, an attacker can pick any `r`, compute `message = Poseidon(r)` off-chain, and set `circomData.emporiumMessage = message`. This makes the "proof" for this path self-consistent and trivially satisfiable by anyone — it proves nothing about ownership of `spendingPublicKey`, `nullifyingPrivateKey`, or any real UTXO/commitment in the tree. The `rootHashHinkal` check in `Hinkal.sol` only verifies the root was *ever* a valid tree root (a public value, not secret), and is not even wired into `MainEVMCircuitMin`'s constraints, so it adds no real authentication either: [4](#0-3) 

With a trivially forgeable proof, `Hinkal.transact` will call into `_externalTransact` → `EmporiumUpgradeable.runAction`. When `stack.signerAddress == address(0)`, `verifyWallet` returns immediately with no signature check at all: [5](#0-4) 

The "Stateless Interaction" branch then executes attacker-chosen `op.endpoint.call{value: op.value}(op.callData)` directly from the Emporium contract, blocking only two specific selectors: [6](#0-5) 

Critically, because `circomData.erc20TokenAddresses.length == 0` in this path, the balance-equality safety net in `runAction` — which is supposed to enforce `balanceChange >= 0` per token and revert on unauthorized outflow — iterates over an **empty array** and performs no check whatsoever: [7](#0-6) 

### Impact Explanation
This breaks the intended equality "a valid Groth16 proof accepted by `Hinkal.transact` implies the caller controls a real shielded spending key / nullifier / signed wallet action." Instead, an unprivileged EOA with no shielded balance and no wallet signature can satisfy `verifyProof(...)` and reach an arbitrary external call executed with `msg.sender == EmporiumUpgradeable`, unconstrained by any balance-equality check. Any ERC20 or ETH balance held by the Emporium contract (e.g., accrued relay fees, fee-token remainders, or funds transiently routed through Emporium) can be moved to an attacker-controlled address via a crafted `op.endpoint.call`. This matches "Critical - proof or nullifier verification bypass" and "High - theft of protocol/relay fees."

### Likelihood Explanation
High for an attacker who understands the codebase: producing the forged proof requires only running the (public) circuit's trusted-setup prover with self-chosen private inputs — no cryptographic break is needed, since the circuit itself omits the authentication constraints. The only remaining barrier is that Emporium must hold a nonzero balance of some asset at call time, which can happen incidentally from fee accumulation or from an attacker first funding Emporium via a legitimate deposit path and then draining it via the forged proof.

### Recommendation
- `MainEVMCircuitMin` must not be used for any path that can trigger arbitrary/state-changing external calls or asset movement; either bind `spendingPublicKey`/EdDSA signature verification into the Min circuit, or disallow the min/zero-token dimension selection whenever `externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID` with attacker-suppliable `ops`.
- Require `stack.signerAddress != address(0)` (i.e., a verified EIP-712 wallet signature) whenever `ops` contains non-empty `callData`/`value`, rather than allowing an unauthenticated "Stateless Interaction" branch.
- Perform the balance-equality safety check independent of `erc20TokenAddresses.length`, e.g., by tracking the full set of tokens/ETH actually touched by `ops`, not only the tokens declared (and provable) in `circomData`.

### Proof of Concept
1. Off-chain: pick random `messageSeed = r`; compute `message = Poseidon(r)` using the same Poseidon parameters as the circuit.
2. Build `circomData` with `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `erc20TokenAddresses = []`, `emporiumMessage = message`, `externalActionMetadata = abi.encode(EmporiumStack{ signerAddress: address(0), ops: [EmporiumOperation{endpoint: <targetToken>, invokeWallet: false, value: 0, callData: transfer(attacker, EmporiumBalance)}] })`.
3. Compute `calldataHash` per `CircomDataBuilder.getHashedCalldata` and set matching `circomData.timeStamp`/`rootHashHinkal` to any previously valid root.
4. Generate a Groth16 proof for `MainEVMCircuitMin` using `messageSeed = r` as the only meaningful private input — this proof will verify since the circuit enforces no signature/nullifier/root constraints.
5. Call `Hinkal.transact(a, b, c, dimensions(tokenNumber=0), circomData)`. `verifyProof` succeeds, `rootHashExists` succeeds trivially, `_externalTransact` invokes `EmporiumUpgradeable.runAction`, `verifyWallet` short-circuits (signerAddress == 0), and the Stateless Interaction executes `transfer(attacker, EmporiumBalance)` from the Emporium contract with no balance-equality check applied (empty `erc20TokenAddresses` loop).

### Citations

**File:** contracts/CircomDataBuilder.sol (L134-161)
```text
    function formInputForCircom(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory) {
        if (
            circomData.externalActionData.externalActionId ==
            HINKAL_EMPORIUM_ACTION_ID &&
            circomData.erc20TokenAddresses.length == 0
        ) {
            return formInputEmporiumMin(circomData);
        } else {
            return formInputNormal(chainId, verifyingContract, circomData);
        }
    }

    function formInputEmporiumMin(
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory input) {
        input = new uint256[](circomData.publicSignalCount);

        uint16 index = 0;

        input[index++] = circomData.emporiumMessage;

        input[index++] = circomData.timeStamp;
        input[index++] = circomData.calldataHash;
    }
```

**File:** circuits/MainEVMCircuitMin.circom (L1-18)
```text

pragma circom 2.1.6;

include "../../node_modules/circomlib/circuits/poseidon.circom";

template MainEVMCircuitMin() {
  // Public inputs:
  signal input outTimeStamp;
  signal input calldataHash;

  // Private inputs:
  signal input messageSeed;

  // outputs:
  signal output message;

  message <== Poseidon(1)([messageSeed]);
}
```

**File:** circuits/MainEVMCircuit.circom (L91-148)
```text
  // verifying signature
  component sigVerifier = SignatureVerifier();
  sigVerifier.spendingPublicKey <== spendingPublicKey;
  sigVerifier.eddsaSignature <== eddsaSignature;
  sigVerifier.signedMessageHash <== signedMessageHash;

  // pinning message to seed
  message <== Poseidon(1)([messageSeed]);

	for (var i = 0; i < tokenCount; i++) {
      // 0) iterate over all token types
      var inTotal = 0;
      var outTotal = 0;

      for(var j=0; j< inputCount; j++) {

        calcInPublicKeys[i][j] = StealthAddressCalculator();
        calcInPublicKeys[i][j].spendingPublicKey <== spendingPublicKey;
        calcInPublicKeys[i][j].nullifyingPrivateKey <== nullifyingPrivateKey;
        calcInPublicKeys[i][j].nullifyingPrivateKeyBits <== nullifyingPrivateKeyBits.out;
        calcInPublicKeys[i][j].H0Ax <== inH0Ax[i][j];
        calcInPublicKeys[i][j].H0Ay <== inH0Ay[i][j];

        // 1) Calculating Commitments for Input UTXOs
        calcCommitment[i][j] = OriginalCommitmentCalculator();
        calcCommitment[i][j].amount <== inAmounts[i][j];
        calcCommitment[i][j].erc20TokenAddress <== erc20TokenAddresses[i];
        calcCommitment[i][j].publicKey <== calcInPublicKeys[i][j].out;
        calcCommitment[i][j].timeStamp <== inTimeStamps[i][j];

        preventInOverflow[i][j] = OverflowPreventer(inputCount);
        preventInOverflow[i][j].in <== inAmounts[i][j];

        // 2) Calculating Nullifier from commitment and signature
        calcSignature[i][j] = Signature();
        calcSignature[i][j].nullifyingPrivateKey <== nullifyingPrivateKey;
        calcSignature[i][j].commitment <== calcCommitment[i][j].out;

        calcNullifier[i][j] = NullifierCalculator();
        calcNullifier[i][j].commitment <== calcCommitment[i][j].out;
        calcNullifier[i][j].signature <== calcSignature[i][j].out;

        // 3) Checking that nullifier is legit
        inNullifiers[i][j] === calcNullifier[i][j].out;

        // 4) Calculating Transaction Root Hash
        calcTransactionRootHash[i][j] = MerkleRootCalculator(treeDepth);
        calcTransactionRootHash[i][j].inCommitment <== calcCommitment[i][j].out;
        for (var k = 0; k < treeDepth; k++) {
          calcTransactionRootHash[i][j].commitmentSiblings[k] <== inCommitmentSiblings[i][j][k];
          calcTransactionRootHash[i][j].commitmentSiblingSides[k] <== inCommitmentSiblingSides[i][j][k];
        }

        // 5) Checking that transaction root hash is legit
        calcEqual[i][j] = ForceEqualIfEnabled();
        calcEqual[i][j].in[0] <== calcTransactionRootHash[i][j].rootHash;
        calcEqual[i][j].in[1] <== rootHashHinkal;
        calcEqual[i][j].enabled <== inAmounts[i][j];
```

**File:** contracts/Hinkal.sol (L44-64)
```text
            require(
                verifyProof(
                    a,
                    b,
                    c,
                    inputForCircom,
                    buildVerifierId(
                        dimensions,
                        circomData.externalActionData.externalActionId
                    )
                ),
                "Invalid Proof"
            );
            // Root Hash Validation
            require(
                rootHashExists(
                    circomData.rootHashHinkal,
                    circomData.rootHashHinkalIndex
                ),
                "Hinkal Root Hash is Incorrect"
            );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L102-118)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-317)
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
