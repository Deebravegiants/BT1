### Title
Front-run / replay of a signed `EmporiumStack` redirects the resulting shielded UTXO to an attacker-chosen stealth address - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
The EIP-712 digest a wallet owner signs for an `EmporiumStack` (`EMPORIUM_SIGNATURE_TYPEHASH`) binds only `emporiumMessage`, the hash of `ops`, `maxFee` and `deadline`; it never binds `circomData.stealthAddressStructure`. `handleOut()` in `EmporiumUpgradeable` builds the resulting shielded UTXO directly from `circomData.stealthAddressStructure`, a field that any unprivileged submitter of the outer `Hinkal.transact()` call fully controls and that the SNARK circuit only checks for internal self-consistency with the prover's own keys, not against the signer's intent.

### Finding Description
The claimed equality — `(assets leaving the victim's wallet, their destination) == (ops, maxFee)` that the victim actually signed — is broken:

- The signed digest is:
```
EMPORIUM_SIGNATURE_TYPEHASH = keccak256("EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)...")
``` [1](#0-0) 
and it is verified in `verifyWallet` using only `circomData.emporiumMessage`, `_hashEmporiumOps(stack.ops)`, `stack.maxFee`, `stack.deadline` — no `stealthAddressStructure`, no `erc20TokenAddresses`, no `amountChanges`. [2](#0-1) 

- `runAction` executes `stack.ops` (which, for `invokeWallet=true`, run through the victim's own wallet via `IHinkalWallet(stack.signerAddress).callHinkalWallet(...)`), measures the resulting Emporium balance change, and calls `handleOut`, which builds the new UTXO directly from `circomData.stealthAddressStructure`:
```
outUtxo = UTXO(uint256(balanceChange), circomData.erc20TokenAddresses[i], circomData.stealthAddressStructure, circomData.timeStamp);
``` [3](#0-2) 

- `circomData.stealthAddressStructure` is submitted as public SNARK input in `formBasicInput` (`H1x`, `H1y`, `stealthAddress`, `H0x`, `H0y`) and is fully at the discretion of whoever submits the outer `Hinkal.transact()` call — anyone can craft this. [4](#0-3) [5](#0-4) 

- Inside the circuit, `outStealthAddress`/`outH1Ax`/`outH1Ay` are derived solely from the *prover's own* `spendingPublicKey`/`nullifyingPrivateKey`/`H0Ax`/`H0Ay` via `StealthAddressCalculator` — there is no signal in `MainEVMCircuit.circom` that ties this to `EmporiumStack`, `stack.signerAddress`, or the ops being authorized. [6](#0-5) 

Because the `EmporiumStack` signature is transported as plain calldata inside `circomData.externalActionData.externalActionMetadata` of the public `Hinkal.transact()` transaction, an attacker observing the mempool (or otherwise obtaining a not-yet-consumed signed `EmporiumStack`) can front-run/replay it in their own transaction: decode the victim's `(v, r, s, signerAddress, ops, maxFee, deadline)`, keep `emporiumMessage`/`ops`/`maxFee`/`deadline` identical (so `verifyWallet` still passes and `usedMessages[emporiumMessage]` is still false), but generate their own SNARK proof with their own `spendingPublicKey`/`H0Ax`/`H0Ay` so that `circomData.stealthAddressStructure` resolves to a key the attacker controls, and possibly zero `amountChanges` (so no ownership of the victim's shielded notes is required). If any op with `invokeWallet=true` moves the victim's on-chain (non-shielded) assets from `stack.signerAddress`'s wallet into the Emporium contract, the resulting balance increase is shielded straight to the attacker's stealth address via `handleOut`.

None of the listed guards catch this:
- `verifyWallet`/`EMPORIUM_SIGNATURE_TYPEHASH` never reference the destination.
- `performHinkalChecks`/`verifyProof`/circuit's `inTotal + amountChanges === outTotal` only enforce numeric balance consistency and that the prover's own key produced `outStealthAddress` — they never require that key to match the intended recipient.
- `rootHashExists`, `insertNullifiers`, slippage/balance equations in `Hinkal.transact` (`balanceDif == amountChanges[i] + utxoAmount`) are purely arithmetic and are satisfied regardless of whose funds fund the balance change.
- `onlyAllowedRecipient` only restricts who may call `EmporiumUpgradeable.runAction` (i.e., must come via `Hinkal`), not who may call `Hinkal.transact()` itself — any EOA may call `Hinkal.transact()`.

### Impact Explanation
An attacker who intercepts a signed, unused `EmporiumStack` (public in the mempool of the victim's own submission, or otherwise obtained without needing the victim's private note/spend key) can redirect value that leaves the victim's Hinkal wallet through Emporium ops into a shielded UTXO owned by the attacker instead of the victim. This is direct theft of funds released by a signed operation — a Critical-severity impact — and is repeatable for every signed `EmporiumStack` an attacker can capture before it is consumed.

### Likelihood Explanation
Requires: (1) a victim who signs an `EmporiumStack` with at least one `invokeWallet=true` op that moves assets out of their wallet into the Emporium contract, and (2) that signed payload becoming visible to an attacker before being consumed on-chain (e.g., via public mempool observation, since the payload travels as plain calldata in `Hinkal.transact`). Given standard MEV/front-running capability (not a privileged role, not a compromised relay — merely observing pending public transactions), this is feasible and cost is limited to gas plus generating a competing proof with attacker-chosen `H0Ax/H0Ay`.

### Recommendation
Bind the output destination to the signed authorization: include `circomData.stealthAddressStructure` (or at minimum its `stealthAddress`/`H1x`/`H1y`) in the `EMPORIUM_SIGNATURE_TYPEHASH` digest that `stack.signerAddress` signs, so that `verifyWallet` rejects any `circomData` whose destination differs from what the signer authorized. Alternatively, require the wallet owner to explicitly co-sign or pre-register the intended recipient stealth address for value released from their own wallet via Emporium ops.

### Proof of Concept
Hardhat test outline:
1. Victim deploys/owns a Hinkal wallet holding an ERC20 balance; victim signs an `EmporiumStack` with one op (`invokeWallet: true`, `endpoint`/`callData` that transfers the wallet's ERC20 balance into the Emporium contract), `maxFee`, `deadline`, `emporiumMessage = M`.
2. Simulate front-running: before this signed payload is ever submitted, an attacker builds `circomData` with the same `externalActionData.externalActionMetadata` (the victim's `v,r,s,signerAddress,ops,maxFee,deadline`), `emporiumMessage = M`, `amountChanges = 0` for all tokens, and their own `stealthAddressStructure` (own `spendingPublicKey`/`H0Ax`/`H0Ay`).
3. Generate a valid SNARK proof for this `circomData` with `snarkjs`/circom witness generator using the attacker's own keys (no nullifier ownership of victim's notes required since `amountChanges = 0`).
4. Call `Hinkal.transact(...)` from the attacker's EOA.
5. Assert: `verifyWallet` succeeds (signature recovers to `stack.signerAddress` == victim), `usedMessages[M]` becomes true, and the resulting inserted UTXO's `stealthAddressStructure`/owner key equals the attacker's key, not the victim's — i.e., `resultUtxo.stealthAddressStructure.stealthAddress != victim-derived stealth address` while `stack.signerAddress == victim` and the ERC20 balance decrease is confirmed to have come from the victim's wallet.
6. Confirm the victim's originally-intended transaction (with victim's own `stealthAddressStructure`) now reverts with `UsedMessage`, proving the value was diverted rather than double-spent.

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

**File:** contracts/CircomDataBuilder.sol (L188-192)
```text
        // 1) First we list public inputs as in the body of the main template (not the one with exact dimensions)
        input[index++] = circomData.stealthAddressStructure.H1x;
        input[index++] = circomData.stealthAddressStructure.H1y;
        input[index++] = circomData.stealthAddressStructure.stealthAddress;
        input[index++] = emporiumMessage; // this is for Emporium message signature verification
```

**File:** contracts/CircomDataBuilder.sol (L236-237)
```text
        input[index++] = circomData.stealthAddressStructure.H0x;
        input[index++] = circomData.stealthAddressStructure.H0y;
```

**File:** circuits/MainEVMCircuit.circom (L80-89)
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
