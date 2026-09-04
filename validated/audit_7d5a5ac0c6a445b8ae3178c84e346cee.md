### Title
Emporium EIP-712 signature omits `erc20TokenAddresses`, `stealthAddressStructure`, `relay`, and `feeStructure` — a captured signed stack can be executed with attacker-chosen `CircomData` to redirect swept wallet funds and fees - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.verifyWallet` only recovers the signer over `(emporiumMessage, ops, maxFee, deadline)` via `EMPORIUM_SIGNATURE_TYPEHASH`, but `runAction` executes the signed `ops` against an entirely separate, unsigned `CircomData` struct that controls the output destination (`stealthAddressStructure`), the token accounting (`erc20TokenAddresses`, `deltaAmountChanges`), and the fee routing (`relay`, `feeStructure.feeToken`). Any unprivileged actor who obtains a valid `(ops, sig, maxFee, deadline, emporiumMessage)` tuple (e.g., intercepted before the intended relay submits it) can wrap it in their own `CircomData` and be the one who calls `Hinkal.transact`, causing the wallet's assets moved by the signed `ops` to be swept into a shielded UTXO under the attacker's own stealth address and fees routed to the attacker's own relay/token.

### Finding Description
The invariant the protocol needs is: *(assets moved out of `stack.signerAddress`'s wallet, their destination) == (ops, maxFee) the owner signed*. This equality is broken because the destination/accounting fields never enter the signed hash.

`EMPORIUM_SIGNATURE_TYPEHASH` binds only: [1](#0-0) 

`verifyWallet` recovers the signer against this narrow payload and only additionally checks `flatFee <= maxFee`; it never touches `circomData.erc20TokenAddresses`, `circomData.stealthAddressStructure`, `circomData.relay`, or `circomData.feeStructure.feeToken`: [2](#0-1) 

The replay guard is keyed on `circomData.emporiumMessage`, which is itself embedded in the signed hash, so it correctly prevents literal replay of the same `(message, ops, maxFee, deadline)` combination: [3](#0-2) 

However `runAction` executes `stack.ops` — which can invoke `IHinkalWallet(stack.signerAddress).callHinkalWallet(...)`, moving the wallet owner's real assets — and then measures balance deltas and packages the resulting output strictly from the caller-supplied `CircomData`: [4](#0-3) [5](#0-4) 

Because `circomData.stealthAddressStructure` determines who owns the resulting shielded UTXO and it is not part of the signature, whoever submits the transaction (any unprivileged party who has obtained the valid `ops`/`sig`/`message` tuple — e.g., by observing it in transit to the intended relay, or being handed it by a wallet owner expecting a specific relay to submit it) can substitute their own `CircomData` with their own `stealthAddressStructure`, their own `relay`, and a `feeStructure.feeToken` of their choosing (bounded only by `flatFee <= maxFee`, not otherwise constrained or committed). The wallet owner authorized *what calls execute*, but never authorized *where the swept funds and the fee end up*. The `usedMessages` replay guard stops the legitimate submitter from also executing it afterward, so the theft is "first submitter wins," not literally an owner-nonce-bound replay guard.

### Impact Explanation
An attacker who front-runs or otherwise obtains a signed `EmporiumStack` before its intended relay can execute it with their own `CircomData`, causing:
- Funds swept out of the wallet owner's `IHinkalWallet` by the signed `ops` to be transferred to `msg.sender`/packaged into a shielded UTXO tagged with the attacker's own `stealthAddressStructure`, i.e., executing calls / moving assets under terms (destination) the owner never signed.
- Relay fees (`flatFee`, up to the signed `maxFee`) directed to an attacker-chosen `relay` and `feeToken` rather than the intended relay/token.

This matches the "High" category: executing calls or moving assets a wallet owner never authorised, and/or theft of protocol/relay fees. It is a single-shot theft per captured signed stack (bounded by `usedMessages`), not an unbounded repeatable drain, but it is fully attacker-triggerable with no privileged role required — only possession of a validly-signed stack destined for someone else.

### Likelihood Explanation
Preconditions: attacker must obtain a validly signed `(ops, sig, maxFee, deadline, emporiumMessage)` before the intended relay submits it (e.g., via mempool observation, or being one of several relays given the signed payload for redundancy). Given that, the attack costs only gas and the ability to construct arbitrary `CircomData` with a valid ZK proof for the accounting fields — well within the stated unprivileged attacker capability set (deposit own funds, craft any `CircomData`, generate own proofs, choose call ordering). No compromise of the signer's key is needed. Feasibility is high whenever signed stacks are distributed to a relay network or otherwise become observable prior to on-chain confirmation.

### Recommendation
Include all fields that determine the disposition of the swept assets and fees in the EIP-712 payload that `verifyWallet` recovers against — at minimum `circomData.erc20TokenAddresses`, `circomData.stealthAddressStructure`, `circomData.relay`, and `circomData.feeStructure` (or a hash/commitment thereof) — so the signer explicitly authorizes the destination and fee terms, not just the raw call list.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, a mock `IHinkalWallet`, and a mock ERC20/endpoint that the signed `ops` will call to move tokens from the wallet into the Emporium contract.
2. Have the wallet owner sign an `EmporiumStack` (`ops`, `maxFee`, far-future `deadline`) intended for `emporiumMessage = M`, expecting `CircomData_A` (with `stealthAddressStructure = ownerStealthAddr`, `relay = relayA`).
3. Before `CircomData_A`/relayA submits, have an unrelated attacker EOA call `Hinkal.transact` → `EmporiumUpgradeable.runAction` with the same `ops`/`sig`/`maxFee`/`deadline`/`emporiumMessage = M`, but attacker-crafted `CircomData_B` where `stealthAddressStructure = attackerStealthAddr` and `relay = attackerRelay`.
4. Assert: `verifyWallet` succeeds (signature check passes since only `ops/maxFee/deadline/message` are checked); the output UTXO / transferred balance change is attributed to `attackerStealthAddr` / `attackerRelay`, not `ownerStealthAddr`/`relayA`; and the later legitimate submission with `CircomData_A` reverts with `UsedMessage()`.
5. Left side of invariant (assets leaving wallet, destination) = (wallet funds, attacker's stealth address/relay); right side (what owner signed) = (ops, maxFee) with no destination commitment — demonstrating the equality is broken.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L36-39)
```text
    bytes32 private constant EMPORIUM_SIGNATURE_TYPEHASH =
        keccak256(
            "EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)EmporiumOperation(address endpoint,bool invokeWallet,uint128 value,bytes callData)"
        );
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-349)
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

        if (block.timestamp > stack.deadline) {
            revert SignatureExpired();
        }

        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
    }
```
