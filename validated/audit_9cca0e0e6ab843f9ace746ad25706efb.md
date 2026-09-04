### Title
Unrestricted `feeRecipient` in `ProoflessFeeStructure` lets caller redirect protocol fee to themselves - ([File: contracts/HinkalWrapper.sol])

### Summary
`HinkalWrapper.prooflessDeposit` accepts a caller-supplied `ProoflessFeeStructure` and calls `_settleFee`, which transfers `feeAmount` of `feeToken` (or ETH) directly to `feeStructure.feeRecipient` with no validation that this address is a protocol-designated treasury. Since a caller can invoke `prooflessDeposit` directly (bypassing any front-end that would normally hardcode the real treasury address), they can set `feeRecipient` to themselves, receive back the "fee" they nominally paid, and still have the deposit forwarded normally to `Hinkal` via `IHinkal(hinkal).prooflessDeposit`.

### Finding Description
The claimed equality — "protocol fee revenue paid == fee revenue that reaches the protocol's designated treasury" — is broken.

Code path: [1](#0-0) 
`prooflessDeposit` calls `_settleFee(feeStructure)` before pulling deposit tokens and forwarding to `Hinkal`. [2](#0-1) 
`_settleFee` unconditionally sends `feeStructure.feeAmount` of `feeStructure.feeToken` (or ETH) to `feeStructure.feeRecipient` — a fully attacker-supplied `calldata` field. [3](#0-2) 
The struct itself has no constraints — `feeRecipient`, `feeToken`, and `feeAmount` are plain fields with no on-chain binding to a treasury address, no signature, no allowlist.

There is no whitelist or allowed-recipient check anywhere in `HinkalWrapper.sol` restricting `feeStructure.feeRecipient` (confirmed by searching the repo for `feeRecipient`/`whitelist`/`onlyAllowedRecipient` patterns — those patterns exist only in unrelated external-action files, not in `HinkalWrapper`). The deposit itself proceeds normally and unaffected through `IHinkal(hinkal).prooflessDeposit`, whose interface (`contracts/types/IHinkal.sol`) takes no fee-related parameters at all — fee logic is entirely the wrapper's responsibility and is not re-checked or constrained by `Hinkal.sol`.

Root cause: the wrapper trusts the caller-supplied `feeRecipient` as if it always reflects an off-chain frontend-computed, honest fee-routing address, with no on-chain enforcement. Any EOA calling the wrapper directly (skipping the frontend) controls this field completely.

Attacker's exact call: invoke `HinkalWrapper.prooflessDeposit(erc20Addresses, amounts, stealthAddressStructures, onChainEncryptedOutputs, createBlockedUtxos, feeStructure, orderId)` with `feeStructure.feeRecipient = attacker`, `feeStructure.feeToken`/`feeAmount` set to whatever values would look "honest" (e.g., matching what the frontend would have used). `_settleFee` sends the fee to the attacker's own address. The deposit into `Hinkal` proceeds identically to a legitimate call — no proof-verification or nullifier logic is affected, since this bug is entirely at the fee-forwarding layer, outside the shielded-value/circuit accounting.

None of the listed guards (`performHinkalChecks`, `verifyProof`, `rootHashExists`, nullifier insertion, circuit constraints) apply here because this fee transfer happens in `HinkalWrapper` before any interaction with `Hinkal`'s proof/nullifier logic — it's a plain ERC20/ETH transfer to an unchecked address.

### Impact Explanation
The protocol/relay permanently loses the fee revenue it expected to collect on this deposit, since the attacker redirects it to themselves (or to `address(0)` / any other sink) instead of the actual treasury. This is a **theft or permanent freezing of protocol/relay fees** by an unprivileged, direct caller, and it is fully repeatable per-transaction with no cost beyond gas — the attacker never actually loses any of their own funds since the "fee" they pay simply comes back to them. This matches the **High** severity category defined by the rules ("theft or permanent freezing of protocol/relay fees").

### Likelihood Explanation
- Preconditions: none beyond the attacker calling `HinkalWrapper.prooflessDeposit` directly instead of through the intended frontend UI — which is trivial since the function is `external` and takes no restricted parameters.
- No special tree/nullifier/action state is required; this works on the very first deposit.
- Attacker cost: gas only. Fully repeatable on every proofless deposit.
- Feasibility: high — this requires no proof generation trickery, no privileged role, and no interaction with circuit constraints at all.

### Recommendation
Do not accept an arbitrary `feeRecipient` from the caller. Either hardcode the protocol treasury address in `HinkalWrapper` (e.g., an immutable/owner-settable `feeRecipient` state variable set via `onlyOwner`), or validate `feeStructure.feeRecipient` against an on-chain allowlist of protocol-designated fee sinks before transferring funds in `_settleFee`.

### Proof of Concept
Foundry test plan:
1. Deploy `HinkalWrapper` pointing at a mock `Hinkal` contract that accepts `prooflessDeposit` calls and simply records the call.
2. Have `attacker` call `HinkalWrapper.prooflessDeposit` with `feeStructure = {feeRecipient: attacker, feeToken: address(0), feeAmount: X}` and `msg.value = depositAmount + X`.
3. Assert: `attacker.balance` after the call equals `attacker.balance` before minus `depositAmount` (i.e., the fee `X` was returned to the attacker rather than reaching any treasury address).
4. Assert: the mock `Hinkal.prooflessDeposit` was called with `ethForHinkal == depositAmount`, i.e., the deposit itself succeeded normally.
5. Assert: balance of the intended protocol fee-sink address (any hardcoded/expected treasury address) remains unchanged (`== 0` increase), proving fee revenue never reached the protocol while the deposit completed as if fees had been paid honestly.

### Citations

**File:** contracts/HinkalWrapper.sol (L28-47)
```text
    function prooflessDeposit(
        address[] calldata erc20Addresses,
        uint256[] calldata amounts,
        StealthAddressStructure[] calldata stealthAddressStructures,
        bytes[] calldata onChainEncryptedOutputs,
        bool createBlockedUtxos,
        ProoflessFeeStructure calldata feeStructure,
        string calldata orderId
    ) external payable {
        uint256 ethForHinkal = _settleFee(feeStructure);
        _pullAndApproveDepositTokens(erc20Addresses, amounts);
        IHinkal(hinkal).prooflessDeposit{value: ethForHinkal}(
            erc20Addresses,
            amounts,
            stealthAddressStructures,
            onChainEncryptedOutputs,
            createBlockedUtxos,
            orderId
        );
    }
```

**File:** contracts/HinkalWrapper.sol (L49-70)
```text
    function _settleFee(
        ProoflessFeeStructure calldata feeStructure
    ) internal returns (uint256 ethForHinkal) {
        ethForHinkal = msg.value;
        if (feeStructure.feeToken == address(0)) {
            require(
                msg.value >= feeStructure.feeAmount,
                "insufficient ETH for fee"
            );
            ethForHinkal = msg.value - feeStructure.feeAmount;
            if (feeStructure.feeAmount > 0) {
                transferETH(feeStructure.feeRecipient, feeStructure.feeAmount);
            }
        } else if (feeStructure.feeAmount > 0) {
            transferERC20TokenFrom(
                feeStructure.feeToken,
                msg.sender,
                feeStructure.feeRecipient,
                feeStructure.feeAmount
            );
        }
    }
```

**File:** contracts/types/ProoflessFeeStructure.sol (L1-8)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.6;

struct ProoflessFeeStructure {
    address feeRecipient;
    address feeToken;
    uint256 feeAmount;
}
```
