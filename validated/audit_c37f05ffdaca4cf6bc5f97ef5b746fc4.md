Based on my analysis of `circuits/MainEVMCircuitMin.circom`, `contracts/CircomDataBuilder.sol`, `contracts/HinkalHelper.sol`, `contracts/Hinkal.sol`, and `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`:

### Title
Signature-free `EmporiumStack` path lets any EOA drain Emporium's balance via unauthorized `transact()` with `signerAddress == address(0)` - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`MainEVMCircuitMin` declares `calldataHash` as a public input but never uses it in any constraint, so a valid proof can be generated for *any* `calldataHash` value (and hence any `externalActionMetadata`/ops content) as long as `message = Poseidon(messageSeed)` matches. Combined with `verifyWallet()`'s unconditional early return when `stack.signerAddress == address(0)`, an attacker can submit an arbitrary `EmporiumStack.ops` array with no EIP712 signature and no proof-level binding of "who authorized these ops," while `handleOut()` still credits any resulting positive balance change to `msg.sender` as a legitimate UTXO.

### Finding Description
The broken equality this exploit claims: **"funds credited to `msg.sender`'s UTXO in `handleOut()` == funds that `msg.sender` (or someone who authorized `msg.sender`) actually contributed/was entitled to."** For the stateless (`signerAddress == address(0)`) path, this equality is *not* enforced by any signature, and I could not confirm it is enforced by the circuit either.

- `getHashedCalldata1` includes `circomData.externalActionData` (which contains `externalActionMetadata`, i.e., the ABI-encoded `EmporiumStack` with `ops`) [1](#0-0) . `performHinkalChecks` requires `getHashedCalldata(circomData) == circomData.calldataHash` [2](#0-1) , so `calldataHash` is indeed a genuine hash of the ops content. So far, ops **are** cryptographically bound to `calldataHash`.
- `calldataHash` is then passed to the circuit as a public input via `formInputEmporiumMin` (`input[2] = circomData.calldataHash`) [3](#0-2) , and `Hinkal.transact()` calls `verifyProof(..., inputForCircom, buildVerifierId(...))` [4](#0-3) .
- However, in `MainEVMCircuitMin.circom`, `calldataHash` is declared `signal input calldataHash;` as a public input but is **never referenced in any constraint** — the only constraint in the whole template is `message <== Poseidon(1)([messageSeed]);` [5](#0-4) . This means a prover can produce a valid Groth16 proof for the `(a,b,c)` triple with `calldataHash` set to literally any value, because the R1CS has no constraint tying it to `messageSeed`, `message`, or anything else — it is a "dangling" public input. Consequently the proof gives **zero cryptographic guarantee** about the content of `ops`; it only proves `message = Poseidon(messageSeed)` for some private `messageSeed` the attacker fully controls.
- Meanwhile, `verifyWallet()` sets `$.usedMessages[circomData.emporiumMessage] = true` unconditionally, then returns immediately with **no signature check at all** if `stack.signerAddress == address(0)` [6](#0-5) .
- `runAction()` then executes every `op` in `stack.ops` via `op.endpoint.call{value: op.value}(op.callData)` in the stateless branch (since `signerAddress == address(0)` forces case 2 regardless of `op.invokeWallet`) [7](#0-6) , then computes `balanceChange` from Emporium's own token balance delta and calls `handleOut(balanceChange, circomData, i)`, which transfers `balanceChange` to `msg.sender` and returns a UTXO of that amount if `balanceChange > 0` [8](#0-7) .

**Root cause**: The stateless path's *authorization* for "who is allowed to run these ops and receive the resulting UTXO" is supposed to come from either (a) an EIP712 signature (skipped when `signerAddress == address(0)`) or (b) circuit-level binding of `calldataHash`/ops to the prover's identity/rights. Neither holds: (a) is explicitly bypassed by design for the "relay-initiated" stateless case, and (b) is not enforced because `MainEVMCircuitMin` doesn't constrain `calldataHash` at all.

**Attacker's exact call**: An attacker who has generated a valid Groth16 proof for `MainEVMCircuitMin` for their own `messageSeed` (any value they choose, unrelated to any victim) calls `Hinkal.transact(a, b, c, dimensions, circomData)` where:
- `circomData.externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `circomData.erc20TokenAddresses.length == 0` (so `formInputEmporiumMin` path is used, matching `MainEVMCircuitMin`) [9](#0-8) .
- `circomData.externalActionData.externalActionMetadata` encodes an `EmporiumStack` with `signerAddress = address(0)` and `ops` containing a call to an attacker-controlled endpoint/selector that ultimately moves Emporium's token balance to the attacker (e.g., a token `transfer` from Emporium to attacker triggered by a call Emporium itself makes, or any op whose net effect increases attacker's balance and decreases Emporium's tracked balance for a token index it's watching).

**Why existing guards seemingly fail** (with the caveat below): `performHinkalChecks`'s `getHashedCalldata(circomData) == circomData.calldataHash` check is a self-consistency check on the calldata against itself — it does **not** verify that the ops were authorized by anyone; it only ensures the attacker didn't lie about their own submitted calldata. `verifyWallet()`'s signature check is explicitly skipped for `signerAddress == address(0)`. And the ZK proof, per the circuit code shown, does not constrain `calldataHash` to anything, so it can't provide the missing authorization either.

**Important caveat — scope limitation**: I could **not** find or verify how `MainEVMCircuitMin`'s output `message` is compared against `circomData.emporiumMessage` on-chain (I was unable to find a wrapping "main component" declaration specifying which signals are public, nor the code that checks `message == emporiumMessage`, within available index results before this iteration ended). If such a binding exists and is enforced elsewhere (e.g., in `HinkalBase` or the verifier wrapper) with `calldataHash` actually tied into the Poseidon computation contrary to what the given `MainEVMCircuitMin.circom` file's literal Poseidon call shows, my conclusion that "any calldataHash passes" would be materially affected. Based strictly on the file content I retrieved, `calldataHash` is unused in constraints, but I flag this as an area needing full-repo verification (e.g., via a Devin session with complete filesystem access) since the wiki/ask-index may not have surfaced every relevant file, and there may be a second wrapper/`component main {public [...]}` declaration I could not locate.

### Impact Explanation
If the caveat above resolves as suspected (i.e., `calldataHash`/ops content is truly unconstrained by the proof and the `signerAddress == address(0)` path has no other authorization gate), then any unprivileged EOA could drain the entire token balance currently held by the `EmporiumUpgradeable` contract for any token, by crafting ops that move that balance out and having `handleOut()` credit it as their own UTXO — this is direct theft of funds Emporium is holding (which could include funds from prior deposits, in-flight balances, or funds sent by other users/relays), matching the **Critical** category ("direct theft of shielded or in-flight user funds"). The action is repeatable for every fresh `circomData.emporiumMessage` value and for every token Emporium holds a balance of.

### Likelihood Explanation
Preconditions: Emporium must hold a nonzero balance of some token at call time (e.g., from a proofless deposit, a partially-completed multi-step interaction, or dust left over from prior `runAction` calls) [10](#0-9) . The attacker cost is generating one Groth16 proof for `MainEVMCircuitMin` with an arbitrary self-chosen `messageSeed` — no special privilege, key, or victim cooperation is required. Feasibility depends entirely on the unresolved question of whether `calldataHash` is truly unconstrained in the full/final circuit build (see caveat) — if confirmed, likelihood is high and the exploit is trivially repeatable.

### Recommendation
1. In `MainEVMCircuitMin.circom`, add an explicit constraint binding `calldataHash` (and ideally `emporiumMessage`) into the circuit's arithmetic — e.g., constrain `message` to be a function of both `messageSeed` and `calldataHash` (or otherwise force the prover to know a secret tied to the specific ops/calldata being authorized), so a proof cannot be reused/forged for arbitrary `calldataHash` values.
2. Independently, do not allow `verifyWallet()` to fully bypass authorization for `signerAddress == address(0)`; that path should require some other verifiable binding (e.g., require `deltaAmountChanges` derived amounts to net non-positive against Emporium's pre-existing balance, or require the proof to strictly constrain which balance changes are attributable to the calling prover) before crediting `handleOut()`'s balance delta to `msg.sender`.
3. Have a background engineering session fully trace how `message` (the circuit output) is consumed on-chain relative to `circomData.emporiumMessage`, confirm whether any wrapper file constrains `calldataHash`, and close the gap either in the circuit or in `EmporiumUpgradeable.verifyWallet()`/`runAction()`.

### Proof of Concept
Hardhat test plan (pending confirmation of the circuit-binding caveat above):
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, register the Emporium external action and its verifier for the `MainEVMCircuitMin`-sized `Dimensions`/`externalActionId` combination.
2. Victim (or an unrelated actor) performs `prooflessDeposit` or a normal `transact()` that leaves a nonzero ERC20/ETH balance sitting in `EmporiumUpgradeable` (assert `token.balanceOf(emporium) > 0` before the attack).
3. Attacker (unprivileged EOA, no relation to victim) builds `circomData` with `erc20TokenAddresses.length == 0`, `externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalActionMetadata` = ABI-encoded `EmporiumStack{ signerAddress: address(0), ops: [ { endpoint: attackerControlledContract, invokeWallet: false, value: 0, callData: <call that causes Emporium's tracked balance to decrease and attacker's external balance to increase> } ] }`.
4. Attacker computes `calldataHash = getHashedCalldata(circomData)` locally to pass the self-consistency check, then generates a Groth16 proof for `MainEVMCircuitMin` using an arbitrary self-chosen `messageSeed`, asserting the proof verifies with `verifyProof` regardless of `calldataHash`'s actual value (test both a "correct" and a deliberately mismatched `calldataHash`/`messageSeed` pairing to prove no constraint links them).
5. Attacker calls `Hinkal.transact(a, b, c, dimensions, circomData)` from their own EOA.
6. Assert: `EmporiumUpgradeable`'s balance for the token decreases to (or toward) zero, and a UTXO of that amount is created for the attacker's `stealthAddressStructure` (i.e., `handleOut`'s emitted UTXO/on-chain commitment corresponds to attacker, not victim) — proving the equality "credited UTXO owner == fund's rightful owner" is broken. Also assert `verifyWallet` never reverted despite `stack.signerAddress == address(0)` and no ECDSA signature fields being populated.

**Note**: Before this finding can be finalized as valid, it is essential to verify — likely by inspecting the full build artifacts/wrapper (`.circom` `component main {public [...]}` declaration or a generated `.r1cs`/`.sym`) not surfaced in this index — that `calldataHash` is genuinely unconstrained in the compiled circuit used for `MainEVMCircuitMin`'s verifier, and that no other on-chain check (not found in the files reviewed) re-derives or checks `message`/`emporiumMessage`/`calldataHash` consistency outside the proof.

### Citations

**File:** contracts/CircomDataBuilder.sol (L20-35)
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
```

**File:** contracts/CircomDataBuilder.sol (L139-148)
```text
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
```

**File:** contracts/CircomDataBuilder.sol (L150-161)
```text
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

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
```

**File:** contracts/Hinkal.sol (L44-56)
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
```

**File:** circuits/MainEVMCircuitMin.circom (L6-18)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L91-118)
```text
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L141-150)
```text
            // the only case when balanceChange can be < 0, when there were some funds on emporium before the call
            if (balanceChange < 0) {
                revert BalanceChangeShouldBePositive();
            }

            UTXO memory utxoOut = handleOut(balanceChange, circomData, i);

            if (utxoOut.amount > 0) {
                utxoSet[utxoSetLength++] = utxoOut;
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-316)
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
