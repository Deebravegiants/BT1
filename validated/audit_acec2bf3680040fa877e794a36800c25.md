### Title
Emporium `verifyWallet` never binds `feeStructure`/`relay` to the owner's signature, letting an attacker drain a wallet in an arbitrary fee token - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`verifyWallet` recovers the EIP‑712 signature over only `EMPORIUM_SIGNATURE_TYPEHASH(message, opsHash, maxFee, deadline)`, and `runAction`/`payRelayFees` then apply `circomData.feeStructure` and `circomData.relay` — fields fully controlled by whoever builds the `CircomData`/proof and never included in the signed payload. `stack.maxFee` is a bare number that is compared directly against `feeStructure.flatFee`, with no binding to `feeStructure.feeToken`, so the numeric cap has no defined unit until the attacker (who chooses `feeToken`, `erc20TokenAddresses`, and `relay`) picks it after the fact.

### Finding Description
The invariant the question describes is: *(assets leaving the wallet, their destination) == (ops, maxFee) the owner signed*. Tracing `verifyWallet`: [1](#0-0) 

the signed hash covers `emporiumMessage`, the hash of `stack.ops` (`endpoint`, `invokeWallet`, `value`, `callData`), `stack.maxFee`, and `stack.deadline`. It does **not** cover `circomData.feeStructure` (feeToken, flatFee, variableRate) or `circomData.relay`, and it does not cover `circomData.erc20TokenAddresses` used elsewhere in `runAction`.

`payRelayFees` is then invoked with the caller-supplied `circomData.feeStructure` and `circomData.relay`: [2](#0-1) 

For the wallet-signed path (`signerAddress != 0`), the only check tying the fee to the signature is `feeStructure.flatFee > stack.maxFee` reverting: [3](#0-2) 

`stack.maxFee` is a plain integer with no token attached in the typed-data schema (`EmporiumSignature(uint256 message, EmporiumOperation[] ops, uint256 maxFee, uint256 deadline)`), so the owner signs "at most N units" without knowing which ERC‑20 those units are denominated in. Because `feeStructure.feeToken` and the entire `erc20TokenAddresses` array used in the fee loop are chosen by whoever assembles `circomData` (the relay/attacker submitting the transaction, not the wallet owner), the attacker can pick a high-value token the wallet holds as `feeToken`, set `flatFee == stack.maxFee`, and have `sendToRelayFromWallet` pull that amount straight from the signer's `IHinkalWallet` via `doSendToRelay` to any `relay` address of the attacker's choosing: [4](#0-3) [5](#0-4) 

The owner authorized only the call operations, a numeric fee ceiling, and a deadline. They never authorized *which token* that fee is paid in, nor *who* receives it (`relay` is unconstrained). This is a genuine gap between what `verifyWallet` checks and what `runAction`/`payRelayFees` act on, matching the question's claim that "verifyWallet covers only (emporiumMessage, ops, maxFee, deadline)" while `feeStructure`/`relay` are acted upon unchecked.

Regarding the "stale historical root" sub-claim: `rootHashExists` explicitly supports historical roots via `roots[_rootIndex]` bounded between `MINIMUM_INDEX` and `m_index`, which is the intended and documented mechanism for allowing proofs generated against older (but still valid) tree states — this is a deliberate design choice, not a broken equality, and I found no code path where an old root enables nullifier or fee logic bypass beyond what's already described above. That part of the question does not identify an independent, exploitable defect within the reachable scope of this file.

### Impact Explanation
An attacker who can construct `CircomData` and generate a valid proof for the Emporium action (using their own UTXOs to satisfy the proof's balance constraints, per the threat model) can cause a wallet owner's `IHinkalWallet` to pay a "flat fee" up to `stack.maxFee` **in any ERC‑20 token the wallet holds and the attacker selects**, sent to **any relay address the attacker chooses**. Because the owner's signature never bound the fee token or the relay recipient, this is value transferred to a destination and in a denomination the owner's EIP‑712 signature never authorized — matching the "High: executing calls or moving assets a wallet owner … never authorised" category. This is repeatable for every distinct signed `emporiumMessage`/ops batch a wallet owner produces (bounded by `usedMessages` per message, but each new signed stack is a fresh opportunity).

### Likelihood Explanation
Preconditions: the wallet owner must have signed an `EmporiumStack` (ops, maxFee, deadline) intending flatFee to be paid in some token/denomination they had in mind, and must hold other valuable ERC‑20 balances in their `IHinkalWallet`. The attacker needs only to be the party assembling `circomData` and generating the proof (any unprivileged relay/prover role, consistent with the stated attacker model) — no special permission is required since `feeStructure`/`relay`/`erc20TokenAddresses` are attacker-supplied calldata fields. This is low-cost and directly reachable through the normal `Hinkal.transact` Emporium entrypoint.

### Recommendation
Include `circomData.feeStructure` (at minimum `feeToken` and `flatFee`) and `circomData.relay` in the EIP‑712 typed data signed by the wallet owner (extend `EMPORIUM_SIGNATURE_TYPEHASH` to include `feeToken` and `relay`, or require `feeToken` to be explicitly enumerated among the ops the owner is allowed to pay in). Alternatively, require `stack` to specify an explicit `feeToken` field that `payRelayFees` must match against `feeStructure.feeToken`, reverting otherwise, so `maxFee` is denominated in a token the signer actually agreed to.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, an `IHinkalWallet` mock holding both `TokenA` (intended fee token) and `TokenB` (high-value token), and a mock `HinkalHelper`.
2. Owner signs an `EmporiumStack` with `ops` performing an innocuous call, `maxFee = 100`, `deadline` in the future, expecting fees in `TokenA`.
3. Attacker builds `CircomData` with `feeStructure = { feeToken: TokenB, flatFee: 100, variableRate: 0 }`, `relay = attackerRelay`, and `erc20TokenAddresses` including `TokenB` with `deltaAmountChanges[i] = -100`.
4. Call `runAction` (via the normal Hinkal transact path with a valid proof over this `circomData`) using the owner's untouched signature.
5. Assert: `verifyWallet` succeeds (only `ops`/`maxFee`/`deadline`/`message` checked) even though `feeStructure.feeToken == TokenB`, not `TokenA`.
6. Assert: wallet's `TokenB` balance decreases by 100 and `attackerRelay`'s `TokenB` balance increases by 100 — i.e., the owner's wallet paid a "fee" in a token and to a recipient never present in the signed `EmporiumSignature` hash, violating `(assets leaving the wallet, destination) == (ops, maxFee signed)`.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L186-199)
```text
    function sendToRelayFromWallet(
        address relay,
        address signerAddress,
        uint256 relayFee,
        address feeToken
    ) internal {
        if (relayFee > 0) {
            IHinkalWallet(signerAddress).doSendToRelay(
                relay,
                relayFee,
                feeToken
            );
        }
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L201-245)
```text
    function payRelayFees(
        CircomData calldata circomData,
        address signerAddress,
        int256[] calldata deltaAmountChanges
    ) internal {
        FeeStructure calldata feeStructure = circomData.feeStructure;

        bool foundToken = false;

        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            // tokens deposited into Emporium are not charged
            if (deltaAmountChanges[i] >= 0) {
                continue;
            }

            address erc20TokenAddress = circomData.erc20TokenAddresses[i];
            bool isFeeToken = erc20TokenAddress == feeStructure.feeToken;

            if (isFeeToken) {
                foundToken = true;
            }

            uint256 relayFee = 0;
            uint256 flatFee = isFeeToken ? feeStructure.flatFee : 0;

            if (signerAddress == address(0)) {
                uint256 sumAbs = uint256(-deltaAmountChanges[i]);

                EmporiumStorageVars storage $ = _getEmporiumStorage();
                relayFee = $._hinkalHelper.calculateRelayFee(
                    sumAbs,
                    flatFee,
                    feeStructure.variableRate
                );
            } else {
                relayFee = flatFee;
            }

            payRelay(
                circomData.relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L262-282)
```text
    function payRelay(
        address relay,
        address signerAddress,
        uint256 relayFee,
        address erc20TokenAddress
    ) internal {
        if (relay == address(0) || relayFee == 0) {
            return;
        }

        if (signerAddress == address(0)) {
            sendToRelay(relay, relayFee, erc20TokenAddress);
        } else {
            sendToRelayFromWallet(
                relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
        }
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L318-348)
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

        if (block.timestamp > stack.deadline) {
            revert SignatureExpired();
        }

        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
```
