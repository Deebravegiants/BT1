### Title
Attacker-signed EmporiumStack with an EOA `signerAddress` causes `doSendToRelay` to silently no-op, letting withheld relay fees be withdrawn by the attacker via `handleOut` - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.runAction` calls `payRelayFees` → `payRelay` → `sendToRelayFromWallet`, which performs `IHinkalWallet(signerAddress).doSendToRelay(...)` regardless of whether `signerAddress` is actually a deployed `HinkalWallet` contract. Since `verifyWallet` only checks that `stack.signerAddress` recovers correctly from an EIP-712 signature (which an attacker can freely produce for any EOA they control), an attacker can set `signerAddress` to their own plain EOA. A high-level Solidity call to a function on an address with no code always returns `success = true` without doing anything, so `doSendToRelay` becomes a silent no-op, the relay fee tokens never leave the Emporium contract's balance, and the leftover amount is picked up by the trailing `balancesAfter - balancesBefore` delta and paid out to `msg.sender` via `handleOut`.

### Finding Description
The broken equality is: **tokens actually forwarded to the relay via `doSendToRelay` must equal the `relayFee` amount subtracted from the withdrawn funds (`deltaAmountChanges`) and excluded from the attacker's output UTXO.**

Trace:
1. `runAction` decodes `stack` from attacker-controlled `circomData.externalActionData.externalActionMetadata` [1](#0-0) .
2. `verifyWallet` only validates that the ECDSA signature over attacker-chosen fields (`emporiumMessage`, ops, `maxFee`, `deadline`) recovers to `stack.signerAddress` [2](#0-1) . An attacker can trivially self-sign with a real private key for any EOA they own — no check exists that `signerAddress` has deployed code or is a legitimate `HinkalWallet`.
3. After the ops loop, `payRelayFees` is invoked unconditionally with `stack.signerAddress`, independent of each op's `invokeWallet` flag [3](#0-2) .
4. `payRelay` routes to `sendToRelayFromWallet(relay, signerAddress, relayFee, feeToken)` whenever `signerAddress != address(0)` [4](#0-3) , which calls `IHinkalWallet(signerAddress).doSendToRelay(relay, relayFee, feeToken)` [5](#0-4) . If `signerAddress` is an EOA (no code), this call executes as a no-code low-level `CALL`, which the EVM treats as an unconditional success with no state changes — the fee tokens are **not** transferred to the relay.
5. `balancesAfter`/`balancesBefore` are then diffed; since the fee amount was never actually moved out, it remains in the Emporium contract's balance and is folded into `balanceChange` for that token [6](#0-5) .
6. `handleOut` transfers this positive `balanceChange` straight to `msg.sender` and creates a new output UTXO for it [7](#0-6) .

The legitimate `HinkalWallet.doSendToRelay` is guarded by `onlyEmporium` and actually calls `sendToRelay` to move ERC20/ETH [8](#0-7) , but nothing in `EmporiumUpgradeable` enforces that `stack.signerAddress` is actually such a deployed wallet — it only enforces a valid signature over attacker-chosen content. Existing guards (`onlyAllowedRecipient`, `verifyWallet`'s signature check, `usedMessages` replay protection, `BalanceChangeShouldBePositive`) do not check code-existence or actual fee settlement at the relay, so none of them prevent this divergence.

### Impact Explanation
The relay never receives its fee for the token being withdrawn from the shielded pool, and the withheld fee amount is instead returned to the attacker as part of their own withdrawal UTXO. This is theft of protocol/relay fees — a High severity impact per the stated categories (no shielded-value minting or double-spend occurs, since the tokens paid back to the attacker were already legitimately debited from the shielded pool via `deltaAmountChanges`; only the fee portion is misappropriated). This is repeatable on every Emporium action that would otherwise pay a non-zero relay fee, as long as the attacker is able to supply their own `signerAddress`/signature (self-authorized, `onlyAllowedRecipient` presumably gates the top-level caller of `runAction`, typically `Hinkal.sol`, not the identity of `stack.signerAddress`).

### Likelihood Explanation
Preconditions are low-cost and fully within attacker control: they need only (a) an EOA they hold a private key for, (b) the ability to self-sign the EIP-712 `EmporiumSignature` struct with that key (standard, no forgery needed), and (c) a withdrawal action with non-zero `flatFee`/relay fee configured for the token. No preimage attacks or exotic ECDSA forgeries are required — the attack in the question's description that hinges on deploying a fake contract at a signature-recoverable address is cryptographically infeasible (EIP-712's hashing prevents targeting arbitrary recovered addresses without knowing the private key), but the simpler variant — using a genuine EOA with no code at all — achieves the same effect because Solidity/EVM calls to code-less addresses silently succeed. This makes the attack fully feasible and repeatable at negligible cost.

### Recommendation
In `sendToRelayFromWallet` (or `verifyWallet`), require that `stack.signerAddress` has deployed code before treating it as a valid `HinkalWallet` (e.g., `require(signerAddress.code.length > 0)`), or better, verify via `IERC165`/`supportsInterface` that the target actually implements `IHinkalWallet`, or track fee-token balance before/after the `doSendToRelay` call specifically and require it to have decreased by exactly `relayFee`, reverting otherwise.

### Proof of Concept
1. Deploy `EmporiumUpgradeable` with a mock `HinkalHelper`/relay and an ERC20 fee token; fund the Emporium contract via a simulated withdrawal so `deltaAmountChanges[i] < 0` for that token, with `feeStructure.flatFee = F > 0`.
2. Attacker (any EOA `A`, holds private key) builds an `EmporiumStack` with `signerAddress = A`, `ops` containing a benign stateless op (`invokeWallet=false`), and signs the EIP-712 digest with `A`'s key — `verifyWallet` passes.
3. Call `runAction`; assert:
   - `relay.balanceOf(feeToken)` unchanged (== 0 increase) — relay never received `F`.
   - Attacker's resulting UTXO `amount` for that token includes the withheld `F` on top of the expected withdrawal remainder — i.e., `utxoOut.amount == expectedWithoutFee + F` instead of `expectedWithoutFee`.
4. Compare against the equality: `relayFee_actually_received_by_relay == relayFee_computed_and_deducted_from_deltaAmountChanges` — assert LHS `== 0` while RHS `== F`, proving the mismatch/fee theft.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L80-83)
```text
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-120)
```text
        payRelayFees(circomData, stack.signerAddress, deltaAmountChanges);
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L132-151)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L318-340)
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
