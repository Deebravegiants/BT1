### Title
Emporium EIP-712 signature omits `relay` and `stealthAddressStructure`, letting an unprivileged party front-run a signed stack to steal the swap output and fee - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`verifyWallet` in `EmporiumUpgradeable.sol` recovers the signer over only `emporiumMessage`, the hash of `stack.ops`, `stack.maxFee`, and `stack.deadline`. It never binds `circomData.relay` (who is paid the flat fee) or `circomData.stealthAddressStructure` (who owns the resulting shielded output note). Because `runAction` is reachable through `Hinkal.transact` by any unprivileged caller who can supply their own `CircomData`, whoever submits a previously-signed `EmporiumStack` first — not necessarily the intended relay/wallet owner — decides where the swap proceeds and the fee end up.

### Finding Description
The signed digest is built as: [1](#0-0) 
It commits to `emporiumMessage`, the ops array (endpoint/invokeWallet/value/callData), `maxFee`, and `deadline` only. The replay guard is purely message-based: [2](#0-1) 

`runAction` decodes the `EmporiumStack` from `circomData.externalActionData.externalActionMetadata`, calls `verifyWallet`, executes the signed ops (which do bind endpoint/calldata/value, so the "attacker router calldata" injection inside the ops themselves is not possible — that part is protected), then computes `balanceChange` on the Emporium contract's own balance and sends it out via `handleOut`: [3](#0-2) 

The destination of the resulting shielded note is `circomData.stealthAddressStructure` — a field of `CircomData` that is *not* part of the signed EIP-712 message and is supplied by whoever calls `Hinkal.transact` for this action. Likewise, `payRelayFees`/`payRelay` send the (maxFee-capped) flat fee to `circomData.relay`, also unsigned: [4](#0-3) 

`onlyAllowedRecipient` only requires `msg.sender` to be the whitelisted caller (i.e. `Hinkal.sol` itself calling into the external action), not that the submitter of the outer transaction be the signer or their delegated relay: [5](#0-4) 

**Broken equality:** the invariant the question requires is `(assets leaving the wallet, their destination) == (ops, maxFee)` that the owner signed. Here, *which token/asset moves* and *the calls executed* are indeed pinned by the signature (ops calldata is hashed), but *where the resulting proceeds land* (`stealthAddressStructure`) and *who is paid the fee* (`relay`) are **not** constrained by the signature at all. Any unprivileged party who obtains the signed `EmporiumStack` (e.g., observed in a public relay's mempool/API, or leaked with a far-future `deadline`) can wrap it in their own `CircomData` — setting `stealthAddressStructure` to their own shielded destination and `relay` to their own address — and submit it to `Hinkal.transact` before the intended submitter does. Because `usedMessages[emporiumMessage]` is a first-come-wins flag, the attacker's submission consumes the message and the legitimate flow reverts with `UsedMessage`, while the attacker walks away with the swap output UTXO and the fee.

### Impact Explanation
- The attacker (any unprivileged party who can observe/obtain a validly signed `EmporiumStack`) can redirect the entire output of a LiFi-style swap authorized by the wallet owner to their own shielded balance, and redirect the relay fee (bounded by `maxFee`) to themselves.
- This is "executing calls or moving assets a wallet owner ... never authorised" — the signer authorized *what calls happen*, not *who receives the proceeds*.
- Matches the **High** severity category: assets/fees moved to a destination the owner's signature never authorized. It is repeatable for every signed stack an attacker can capture before its legitimate execution.

### Likelihood Explanation
- Preconditions: a valid, unexpired `EmporiumStack` signature must exist and be observable by the attacker before the legitimate party submits it (e.g., leaked via a public relay/broadcast channel, or a far-future `deadline` giving a wide execution window).
- Cost: only gas to call `Hinkal.transact` first with attacker-chosen `relay`/`stealthAddressStructure`; no special privilege required.
- Feasibility is high given `deadline` can be set arbitrarily far in the future and nothing ties the message's execution to the original submitter's identity or destination.

### Recommendation
Include `circomData.relay` and `circomData.stealthAddressStructure` (or a hash/commitment of them) in the EIP-712 typed data signed by the wallet owner, so the signature fixes both the fee recipient and the output-note owner, not just the ops/maxFee/deadline. Alternatively, require that `msg.sender`/`originalSender` of the outer `Hinkal.transact` call match an address bound into the signed stack (e.g., an authorized submitter field), preventing an unrelated party from front-running execution with self-serving `CircomData`.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable` + `HinkalWallet`, fund the wallet with token `T`.
2. Owner signs an `EmporiumStack` with `ops` = [swap `T`→`U` via a mock router, output recipient = Emporium contract], `maxFee`, far-future `deadline`, and a fixed `emporiumMessage`.
3. Build `CircomData` #1 with `stealthAddressStructure` = owner's stealth address and `relay` = the intended relay; do NOT submit it yet.
4. As a second, unrelated `attacker` address, build `CircomData` #2 using the same `emporiumMessage`/`externalActionMetadata` (same signed stack) but `stealthAddressStructure` = attacker's own address and `relay` = attacker.
5. Call `Hinkal.transact` (or directly `runAction` through the allowed-recipient path) with `CircomData` #2 first.
6. Assert: `usedMessages[emporiumMessage] == true`; the swap executes; the resulting output UTXO is minted to attacker's `stealthAddressStructure` and the fee is paid to attacker's `relay`.
7. Assert: submitting `CircomData` #1 afterward reverts with `UsedMessage`, proving the legitimate flow was pre-empted and the owner's signed authorization on ops/maxFee was fulfilled but the proceeds/fee went to an address the owner never signed over — breaking the equality `(assets, destination) == (ops, maxFee) signed`.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L239-260)
```text
            payRelay(
                circomData.relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
        }

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
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L308-316)
```text
        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;

        if (stack.signerAddress == address(0)) {
            return;
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

**File:** contracts/external-actions/ExternalActionBaseUpgradeable.sol (L39-46)
```text
    modifier onlyAllowedRecipient() {
        ExternalActionBaseStorage storage $ = _getExternalActionBaseStorage();
        require(
            $._isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }
```
