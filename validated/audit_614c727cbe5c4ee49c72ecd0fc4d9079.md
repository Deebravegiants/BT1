### Title
Duplicate fee-token legs in `erc20TokenAddresses` let a relay double-charge `feeStructure.flatFee` from the signer's wallet beyond the EIP-712 signed `maxFee` cap - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`verifyWallet` binds the EIP-712 signature only to `(emporiumMessage, ops, maxFee, deadline)` and separately checks `feeStructure.flatFee <= stack.maxFee` a single time, treating `flatFee` as a one-time charge. `payRelayFees` instead applies `flatFee` once per array index that matches the fee token with a negative `deltaAmountChanges` entry, so when the fee token appears more than once among `circomData.erc20TokenAddresses` with negative deltas (a legitimate multi-leg same-token scenario), the wallet is charged `flatFee` multiple times while the signature only authorised a single `flatFee <= maxFee`.

### Finding Description
The invariant the owner expects is: total relay fee taken from the signer's wallet ≤ `stack.maxFee` (the value the owner signed via EIP-712). The code instead enforces only: [1](#0-0) 
a single per-transaction comparison of `feeStructure.flatFee` (not the aggregate fee actually paid) against `stack.maxFee`.

The actual fee payment loop in `payRelayFees` charges `flatFee` independently for every index where the token matches `feeStructure.feeToken` and the leg is a net outflow (`deltaAmountChanges[i] < 0`): [2](#0-1) 

For `signerAddress != address(0)` (stateful/wallet mode, the path relevant here), `relayFee = flatFee` is used verbatim for every matching leg — there is no running total that is compared against `maxFee`. If `circomData.erc20TokenAddresses` contains the fee token twice, each occurrence with a negative `deltaAmountChanges` entry (e.g. a same-token intermediate/final leg from a multi-hop Emporium op sequence executed against the wallet), `payRelay` → `sendToRelayFromWallet` → `IHinkalWallet(signerAddress).doSendToRelay(...)` is invoked twice, pulling `2 * flatFee` (or more, for N duplicate legs) out of the signer's wallet, while `verifyWallet` only ever validated a single `flatFee ≤ maxFee`.

The EIP-712 signature itself covers only `ops`, `maxFee`, and `deadline` — it never binds `circomData.erc20TokenAddresses`, `circomData.amountChanges`/`deltaAmountChanges`, or `circomData.feeStructure` at all: [3](#0-2) 
so the number and arrangement of fee-token legs is entirely determined by whoever submits the `transact` call (any unprivileged relay/caller with a valid ZK proof for the accompanying CircomData), not by anything the signer approved. Because `runAction` derives `deltaAmountChanges` purely from `circomData.amountChanges` (validated by the proof for consistency of the shielded state, not for the fee semantics), an attacker who has obtained a validly-signed `EmporiumStack` can pair it with a `CircomData`/proof whose `erc20TokenAddresses` list duplicates the fee token across two negative-delta legs, causing the flat fee to be extracted twice from the signer's wallet — money the signer's EIP-712 signature never authorised beyond `maxFee`.

None of the existing guards catch this: `verifyWallet`'s `flatFee > maxFee` check is a single-shot, not cumulative, comparison; `runAction`'s post-call balance/utxo accounting only guarantees `balanceChange >= 0` per token, which is fully satisfied since the doubled fee is still consistent with the actual balance draining that occurred; and the ZK proof does not encode any relationship between "number of legs for the fee token" and "signed maxFee", since that binding lives entirely in the off-chain EIP-712 message which was never designed to cover per-leg fee multiplicity.

### Impact Explanation
A relay/attacker can extract more than the wallet owner authorised (`stack.maxFee`) from the owner's `IHinkalWallet`, by structuring the accompanying `CircomData` so the fee token appears in more than one negative-delta leg. This is a temporary/high-severity theft of the wallet owner's assets to the fee-taking relay, executed under a fee-charge sequence the owner's EIP-712 signature never authorised — matching "High: executing calls or moving assets a wallet owner ... never authorised" / theft of protocol-relay fees beyond the signed cap. It is repeatable for every signed `EmporiumStack` that includes a multi-leg same-token route, up to `N * flatFee` for `N` duplicate legs, each time the attacker (as the transaction submitter/relay) chooses to submit it that way.

### Likelihood Explanation
Preconditions: the attacker must be able to submit a `transact` call carrying a validly signed `EmporiumStack` (`signerAddress != address(0)`) together with a self-crafted `CircomData`/proof that lists the fee token more than once among `erc20TokenAddresses` with negative `deltaAmountChanges` for those entries — something entirely within an unprivileged relay's/caller's control, since `erc20TokenAddresses`/`amountChanges` are not part of the signed EIP-712 payload. Any scenario involving genuine multi-leg routes through the same token (e.g., token used as both intermediate and final asset in a swap sequence) provides a natural cover for this duplication, and the attacker's only cost is generating a valid proof for their own chosen `CircomData` shape — no special role or victim cooperation is required.

### Recommendation
Bind the fee terms to the signature: include `feeStructure` (or at minimum `flatFee`, `variableRate`, `feeToken`) and `relay` in the EIP-712 typed struct that `verifyWallet` verifies. Additionally, change the `flatFee <= maxFee` check into a check on the *aggregate* fee actually charged across all matching legs in `payRelayFees` (e.g., accumulate total flat fee charged for the fee token across the loop and compare the sum, not `feeStructure.flatFee` in isolation, against `stack.maxFee`), so a wallet cannot be billed more than the signed cap regardless of how many legs reference the fee token.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable` with a mock `IHinkalHelper`, mock `IHinkalWallet` (signer's wallet) pre-funded with the fee token, and a mock allowed recipient/relay.
2. Have `signerAddress` (a test EOA) sign an `EmporiumStack` with `ops` = a harmless no-op sequence, `maxFee = F`, `deadline` in the future, via `EIP712` `EMPORIUM_SIGNATURE_TYPEHASH`.
3. Build `CircomData` with `feeStructure.flatFee = F`, `feeStructure.feeToken = TOKEN`, `erc20TokenAddresses = [TOKEN, TOKEN]` (duplicate), and `amountChanges`/resulting `deltaAmountChanges = [-x, -y]` (both negative) for both entries so `payRelayFees` treats both as fee-token outflow legs.
4. Call `runAction` (via the `Hinkal.transact` path, mocking `performHinkalChecks`/proof verification to succeed) with this stack.
5. Assert: wallet's fee-token balance decreased by `2*F` (not `F`), i.e. `signerWallet.balanceBefore - signerWallet.balanceAfter == 2*F > stack.maxFee (=F)`, proving the signer paid more than the EIP-712-signed `maxFee`, violating the invariant `(assets leaving wallet) == (ops, maxFee) the owner signed`.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L210-245)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L318-328)
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L346-348)
```text
        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
```
