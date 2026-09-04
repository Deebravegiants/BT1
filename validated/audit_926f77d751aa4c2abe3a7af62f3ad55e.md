### Title
Unsigned `feeStructure.feeToken` lets an attacker redirect Emporium relay-fee debits to any ERC20 the signer's wallet holds - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.verifyWallet` signs only `emporiumMessage`, the hash of `stack.ops`, `stack.maxFee`, and `stack.deadline` under `EMPORIUM_SIGNATURE_TYPEHASH`; `circomData.feeStructure` (including `feeToken`) is never part of the signed digest. An attacker who obtains a validly signed `EmporiumStack` can resubmit it with the ops/maxFee/deadline untouched but with `feeStructure.feeToken` swapped to any other ERC20 the victim's `HinkalWallet` holds, causing `payRelayFees` to pull `flatFee` of that arbitrary token from the wallet via `doSendToRelay`.

### Finding Description
The broken equality: **AUTHORITY** (the ERC20 token the signer authorized to be spent as a fee) **≠** (the ERC20 token actually debited from the wallet in `sendToRelayFromWallet`).

The EIP-712 digest computed in `verifyWallet` is: [1](#0-0) 

It covers `emporiumMessage`, `_hashEmporiumOps(stack.ops)`, `stack.maxFee`, and `stack.deadline` only. `feeStructure` (holding `feeToken`, `flatFee`, `variableRate`) lives in `CircomData`, entirely outside the `EmporiumStack` struct that gets signed, and only appears folded into `calldataHash` via `CircomDataBuilder.getHashedCalldata2`: [2](#0-1) 

`calldataHash` is an unconstrained public input chosen by whoever generates the proof (the attacker, in this scenario, since they act as their own prover) - it is never checked against anything the wallet owner signed, so it provides no binding on `feeToken`.

The only numeric check on the fee is `flatFee > stack.maxFee` revert: [3](#0-2) 

Critically, `payRelayFees` has a fallback branch that pays the fee in `feeStructure.feeToken` even when that token is **not** part of `circomData.erc20TokenAddresses` (i.e. not part of the signed `ops`' token set at all), as long as `signerAddress != address(0)`: [4](#0-3) 

This calls `payRelay` → `sendToRelayFromWallet` → `IHinkalWallet(signerAddress).doSendToRelay(relay, flatFee, feeToken)`: [5](#0-4) 

`doSendToRelay` on the victim's `HinkalWallet` executes unconditionally for any caller that is `emporium` (`onlyEmporium`), transferring the wallet's own balance of `erc20TokenAddress` directly, with no check that this token relates to any signed operation: [6](#0-5) [7](#0-6) 

Exploit flow: the attacker intercepts (or is handed, as an untrusted relay/prover) a legitimately signed `EmporiumStack` (`v,r,s`, `ops`, `maxFee`, `deadline`, `emporiumMessage`) intended for some DeFi action with an intended fee token. The attacker leaves the signed fields untouched (so `verifyWallet`'s ECDSA check still passes) but crafts their own `CircomData.feeStructure = {feeToken: victimToken2, flatFee: X <= stack.maxFee, variableRate: ...}`, builds their own proof (since they control every unsigned/private field of `CircomData`), and calls `Hinkal.transact` → `EmporiumUpgradeable.runAction` → `payRelayFees` → `sendToRelayFromWallet` → `doSendToRelay`. The wallet is debited `X` units of `victimToken2`, a token never referenced by the signed `ops` and never bound by the signature.

Existing guards do not stop this: `verifyWallet`'s signature check is satisfied because `feeToken` isn't in the signed struct; the `flatFee > maxFee` check only bounds a raw numeric amount, not which token it is denominated in; and `foundToken` logic in `payRelayFees` explicitly permits paying the fee in a token absent from `erc20TokenAddresses`.

### Impact Explanation
The attacker can force the victim's `HinkalWallet` to pay a relay fee denominated in any ERC20 token the wallet holds, up to `stack.maxFee` in raw units - independent of that token's decimals or value, and independent of what token the signer intended for fee payment. Since `flatFee` is a raw integer with no per-token value normalization, picking a low-decimal, high-value token (e.g., an 8-decimal token vs. an intended 18-decimal stablecoin) lets the attacker extract value far exceeding what the signer economically authorized. This is theft of relay/protocol fees and an action (moving a specific asset) that the wallet owner/prover never authorized via signature - matching the High severity category ("theft ... of protocol/relay fees ... executing calls or moving assets a wallet owner or prover never authorised"). It is repeatable each time a new signed `EmporiumStack` for that wallet is intercepted/reused, up to `usedMessages[emporiumMessage]` becoming true (one exploit per unique, previously-unused signed stack the attacker can obtain).

### Likelihood Explanation
Requires: (1) the attacker obtains a validly signed `EmporiumStack` for the victim's `HinkalWallet` (e.g., by acting as or intercepting an untrusted relay/prover flow, which the audit scope explicitly allows attackers to do since they can craft/relay proofs), (2) the victim wallet holds a nonzero balance of some other ERC20 token not part of the signed ops. Both are plausible operational conditions for any wallet actively used with Emporium. The attacker's cost is generating one additional proof, which is cheap and fully within their control since `feeStructure` isn't a circuit-constrained public commitment tied to the signature. The attack is deterministic, not probabilistic, and directly reachable through the documented external entry point `Hinkal.transact`.

### Recommendation
Include `feeStructure` (at minimum `feeToken`, ideally also `flatFee`/`variableRate` bounds) inside the EIP-712 struct hashed and signed in `verifyWallet` (i.e., add it to `EMPORIUM_SIGNATURE_TYPEHASH` and the corresponding `abi.encode` in the signed digest), so that the signer explicitly authorizes which token can be debited as a fee. Additionally, in `payRelayFees`, remove or tighten the fallback branch (lines 247-259) that allows fee payment in a token outside `circomData.erc20TokenAddresses`, or require that `feeStructure.feeToken` be present in the signed op's token set.

### Proof of Concept
Hardhat test plan:
1. Deploy `HinkalWallet` for a victim signer; fund it with `TokenA` (intended fee token, referenced by `ops`) and `TokenB` (unrelated token the wallet also holds).
2. Have the victim EOA sign a valid `EmporiumStack` (`ops` referencing only `TokenA`, `maxFee = M`, `deadline`, `emporiumMessage = msg1`) per `EMPORIUM_SIGNATURE_TYPEHASH`.
3. As the attacker, build `CircomData` with the same `externalActionMetadata` (unchanged signed `EmporiumStack` bytes) but set `circomData.feeStructure = {feeToken: TokenB, flatFee: M, variableRate: 0}`, generate a locally-produced proof for this `circomData`.
4. Call `Hinkal.transact` with this proof/`circomData`.
5. Assert before/after: `TokenB.balanceOf(wallet)` decreases by `M` and `TokenB.balanceOf(relay)` increases by `M`, even though `TokenA` is the only token referenced in the signed `ops`/`erc20TokenAddresses` set and `TokenB` never appears in the EIP-712 signed digest (equality check: signed digest recomputed off-chain excludes `feeStructure`; recovered signer address still equals `stack.signerAddress` despite `feeToken` change) — confirming the fee-token substitution succeeds without invalidating the signature.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L247-259)
```text
        if (!foundToken && feeStructure.flatFee != 0) {
            require(
                signerAddress != address(0),
                "Gas Token in Emporium is not found"
            );

            payRelay(
                circomData.relay,
                signerAddress,
                feeStructure.flatFee,
                feeStructure.feeToken
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

**File:** contracts/CircomDataBuilder.sol (L37-54)
```text
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

**File:** contracts/external-actions/emporium/HinkalWallet.sol (L36-42)
```text
    function doSendToRelay(
        address relay,
        uint256 actualAmount,
        address erc20TokenAddress
    ) external onlyEmporium {
        sendToRelay(relay, actualAmount, erc20TokenAddress);
    }
```

**File:** contracts/Transferer.sol (L178-190)
```text
    function sendToRelay(
        address relay,
        uint256 actualAmount,
        address erc20TokenAddress
    ) internal {
        if (relay != address(0) && actualAmount > 0) {
            transferERC20TokenOrETH(
                erc20TokenAddress,
                relay,
                uint256(actualAmount)
            );
        }
    }
```
