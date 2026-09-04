Confirms `sendToRelay`/`sendToRelayFromWallet` directly transfer `feeToken`'s balance from the wallet, and `circomData.relay`, `erc20TokenAddresses`, `feeStructure` are all outside the EIP-712 signed hash. This is sufficient to finalize.

### Title
Emporium fee token substitution drains wallet's arbitrary ERC20 balance under a signature that never binds `feeStructure.feeToken` - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.verifyWallet` recovers the wallet-owner's EIP-712 signature over only `circomData.emporiumMessage`, `_hashEmporiumOps(stack.ops)`, `stack.maxFee`, and `stack.deadline`; `circomData.feeStructure.feeToken`, `circomData.relay`, and `circomData.erc20TokenAddresses` are never part of the signed digest. Because `payRelayFees` reads `circomData.feeStructure` directly from unsigned calldata and calls `sendToRelayFromWallet` → `IHinkalWallet(signerAddress).doSendToRelay(relay, relayFee, feeToken)`, anyone who obtains a validly-signed `(ops, maxFee, deadline, emporiumMessage)` tuple can resubmit it with a different `feeToken`/`relay`/`erc20TokenAddresses`, redenominating `stack.maxFee` in whatever ERC20 the wallet holds and draining that balance to an attacker-chosen relay.

### Finding Description
Equality that should hold but doesn't: (the fee token/relay/token-list the wallet owner implicitly authorised when computing `maxFee`) == (the fee token/relay `payRelayFees` actually uses to drain `stack.signerAddress`'s wallet).

The signed digest is built in `verifyWallet`: [1](#0-0) 
Only `emporiumMessage`, the ops hash, `maxFee`, and `deadline` are bound. `feeStructure` is fully unconstrained by the signature; the only check on it is a magnitude bound, not a token-identity bound: [2](#0-1) 

Once `verifyWallet` passes, `payRelayFees` iterates `circomData.erc20TokenAddresses` (also unsigned) and for any index where `deltaAmountChanges[i] < 0`, checks if that token equals `feeStructure.feeToken`, and if so pays `flatFee` of that token straight from the wallet's balance: [3](#0-2) 
`sendToRelayFromWallet` then calls the wallet contract to push `feeToken` out to `circomData.relay` (also unsigned): [4](#0-3) 
and `HinkalWallet.doSendToRelay` performs a direct `IERC20.transfer` of that token from the wallet's own on-chain balance: [5](#0-4) [6](#0-5) 

Attack: a wallet owner signs a stack with fixed `ops`, `maxFee=X`, `deadline` (as required — these three fields are cryptographically bound and cannot be altered). An unprivileged party who observes this signed tuple (e.g. in a public relay queue, or simply anyone who can reconstruct/replay it before the legitimate `emporiumMessage` is marked used) resubmits `transact` with the **same** `(ops, maxFee, deadline, emporiumMessage)` but a different `circomData.erc20TokenAddresses` list (including a valuable token the wallet holds, e.g. WBTC) and `circomData.feeStructure = {feeToken: WBTC, flatFee: X, variableRate: 0}`, plus `circomData.relay` set to an address they control. The attacker funds a negligible negative `deltaAmountChanges` entry for that token from proofs over *their own* UTXOs (permitted per the threat model), which is enough to satisfy `deltaAmountChanges[i] < 0` and enter the fee branch. `verifyWallet` still recovers correctly since none of the changed fields are in the signed hash, so `flatFee (=X) <= maxFee (=X)` passes trivially. `payRelayFees` then drains `X` raw units of WBTC (not the token/denomination the signer assumed) from the wallet to the attacker's `relay` address — an amount that can represent value far beyond what the signer intended when picking the numeric `maxFee`.

None of the existing guards catch this: `performHinkalChecks`/`onlyAllowedRecipient` only gate who calls `runAction` (must be Hinkal itself), not what `feeStructure`/`relay` values are used; the ZK proof only proves the caller's own witness is self-consistent with `calldataHash` (which does include `feeStructure`, `relay`, and `erc20TokenAddresses` — see `getHashedCalldata2`/`getHashedCalldata1` in `CircomDataBuilder.sol`), but that only binds the prover's own proof to their own calldata, saying nothing about the wallet owner's authorization, since the prover here is the attacker exploiting their own UTXOs, not the wallet owner. The EIP-712 signature — the only artifact that is supposed to represent the wallet owner's consent — never covers `feeToken`, `relay`, or `erc20TokenAddresses`.

### Impact Explanation
This is theft of a wallet's held ERC20 funds via a token/denomination the signer never authorised, drained to an attacker-controlled `relay` address — matching the High severity category "theft or permanent freezing of protocol/relay fees" / "moving assets a wallet owner ... never authorised." The amount stolen per transaction is bounded by `maxFee` raw units of whatever ERC20 the attacker selects as `feeToken`, up to the wallet's full balance of that token, and is repeatable for every distinct `emporiumMessage` the owner signs (each message can only be consumed once due to `usedMessages`, but the race/front-run applies to every new signed stack).

### Likelihood Explanation
Requires the attacker to obtain a validly-signed `(ops, maxFee, deadline, emporiumMessage)` tuple before it is consumed (e.g. observing it in a public relay/mempool and front-running with a modified `circomData`), and to be able to produce a valid ZK proof over their own UTXOs that funds a negligible negative delta for the target token so it enters the fee loop. Both are within the stated unprivileged-attacker capabilities (deposit own funds, generate own proofs, craft every `CircomData` field). The wallet must hold a non-trivial balance of some ERC20 for the attack to be worthwhile, which is the normal state for an active Emporium wallet.

### Recommendation
Include `feeStructure.feeToken`, `flatFee`, `variableRate`, `relay`, and `erc20TokenAddresses` (or a hash of them) inside `EMPORIUM_SIGNATURE_TYPEHASH`'s signed digest in `verifyWallet`, so the wallet owner's signature fully constrains which token and how much can be pulled as a relay fee, and to whom.

### Proof of Concept
Hardhat test:
1. Deploy `EmporiumUpgradeable`, a `HinkalWallet` for a signer EOA, mint the wallet a large balance of `TokenA` (valuable) and a small balance of `TokenB` (cheap, intended fee token).
2. Have the signer produce an `EmporiumStack` (fixed `ops`, `maxFee = X`, `deadline`) and sign it via `_hashTypedDataV4`/`EMPORIUM_SIGNATURE_TYPEHASH`, intending `feeStructure.feeToken = TokenB`.
3. Submit `transact` once with `circomData.feeStructure.feeToken = TokenA`, `erc20TokenAddresses` including `TokenA` with a crafted negative `deltaAmountChanges` entry, `flatFee = X`, and `relay = attacker`, reusing the exact same `(ops, maxFee, deadline, emporiumMessage)` signature bytes.
4. Assert `verifyWallet` does not revert (signature still recovers correctly) and assert `TokenA.balanceOf(wallet)` decreases by `X` while being sent to the attacker-controlled `relay`, i.e. assert (fee token/amount the signer assumed) != (fee token/amount actually drained), proving the signature never constrained `feeToken`.

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
