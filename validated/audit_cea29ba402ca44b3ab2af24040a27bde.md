## Finding: Valid — Signature does not bind `feeStructure`/`relay`, allowing fee terms outside signer intent

### Title
EIP‑712 `EmporiumSignature` omits `feeStructure`/`relay`, letting the executor pick an unauthorized fee token/destination for the flat fee - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`verifyWallet` recovers the signer over `(emporiumMessage, ops-hash, maxFee, deadline)` only [1](#0-0) , never over `circomData.feeStructure` or `circomData.relay`. The only guard tying the fee to the signature is a raw numeric comparison `feeStructure.flatFee > stack.maxFee` [2](#0-1) , with no binding of which token or which relay address receives the deduction.

### Finding Description
The broken equality is: **(fee token, fee recipient) the owner authorised == (fee token, fee recipient) actually charged**. The `EMPORIUM_SIGNATURE_TYPEHASH` struct is `EmporiumSignature(uint256 message, EmporiumOperation[] ops, uint256 maxFee, uint256 deadline)` [3](#0-2) . `maxFee` is a bare, tokenless integer; there is no field committing to `feeStructure.feeToken`, `feeStructure.variableRate`, or `circomData.relay`.

In `payRelayFees`, once `verifyWallet` passes, the contract iterates `circomData.erc20TokenAddresses` and for whichever entry equals `feeStructure.feeToken`, deducts `flatFee` from the wallet leg and forwards it to `circomData.relay` via `sendToRelayFromWallet` -> `IHinkalWallet(signerAddress).doSendToRelay(relay, relayFee, feeToken)` [4](#0-3) . Both `feeToken` and `relay` are supplied fresh in `circomData` at call time, and neither is constrained by anything the signer put their name to — only the raw numeric comparison to `maxFee` applies [2](#0-1) .

Because `maxFee` has no unit/decimals context, an executor holding a validly-signed `EmporiumStack` can select, among the tokens present in `circomData.erc20TokenAddresses` for that call, whichever token is most valuable and set it as `feeStructure.feeToken` with `flatFee` set to the same nominal number the signer capped (e.g. `maxFee = 1000`). If the signer assumed the fee would be levied in a low-value/high-decimal token but the executor sets `feeToken` to a high-value/low-decimal token in the same numeric amount, the extracted value can be far larger than what the signer intended to authorise — this is exactly the case flagged in the question: "`feeStructure.feeToken` equals the affected token where flat/variable fee deduction overlaps the leg." Likewise, `circomData.relay` (the destination of the fee) is entirely unauthenticated by the signature, so the party executing the call decides who receives the fee.

The variable-fee vector is mitigated in the signed-wallet path itself: when `signerAddress != address(0)`, `payRelayFees` always uses `relayFee = flatFee` and ignores `feeStructure.variableRate` [5](#0-4) ; variable-rate fees only apply on the `signerAddress == address(0)` branch, which is not gated by an EIP‑712 signature at all (that branch's authorization model relies on the ZK proof/`calldataHash` binding shown in `CircomDataBuilder.getSignedMessageHash`/`getHashedCalldata2`, which does include `feeStructure` [6](#0-5) ). So the residual, unmitigated gap is specifically the flat-fee token/destination selection in the wallet-signed branch.

### Impact Explanation
The wallet owner's signature caps only a raw number, not a token or recipient. This lets whoever executes the (validly signed) `EmporiumStack` steer the flat fee to an unintended, potentially higher-value token leg and to an unintended relay address, extracting value or redirecting fees the owner never explicitly authorised for that token/destination. This matches the "High" category: theft/misdirection of protocol or relay fees, and moving assets under terms the owner's signature never covered. It does not reach "Critical" because it is bounded by the numeric `maxFee` ceiling and confined to fee amounts, not the full op value.

### Likelihood Explanation
Preconditions: attacker must be the party executing a legitimately-signed `EmporiumStack` (e.g., the entity submitting the `Hinkal.transact` call with the accompanying proof/CircomData), which is within the described attacker capability set (crafting every field of `CircomData`). No special role, no whitelist bypass, and no proof forgery is required — only free choice of `feeStructure.feeToken`/`relay` at submission time, since these fields sit outside both the EIP‑712 digest and the circuit's amount-conservation constraints tied to the signer. This is repeatable per signed stack (one exploitation per `emporiumMessage`, since replay is blocked by `usedMessages`).

### Recommendation
Include `feeStructure.feeToken`, `feeStructure.variableRate`, and `relay` (or a hash of the whole `CircomData.feeStructure`/`relay`) inside the `EMPORIUM_SIGNATURE_TYPEHASH` digest that the wallet owner signs, so `verifyWallet` cryptographically binds the fee token and fee recipient to the signer's intent, not just a token-agnostic numeric cap.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, a mock `IHinkalWallet`, and two ERC20 tokens (`TokenA` low value, `TokenB` high value).
2. Owner signs an `EmporiumStack` with `maxFee = 1000`, expecting fee to be charged in `TokenA`.
3. Construct `CircomData` with `feeStructure.feeToken = TokenB`, `flatFee = 1000`, `relay = attacker`.
4. Call `runAction`; assert `verifyWallet` succeeds (only checks `1000 <= 1000`).
5. Assert `TokenB` balance moved from signer's wallet to `attacker`-controlled relay equals `1000 * 10^(TokenB decimals)` in value, vastly exceeding what the signer intended when mentally pricing `maxFee=1000` against `TokenA`.
6. Assert equality `(feeToken, relay) signed == (feeToken, relay) executed` is false — proving the gap.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L36-39)
```text
    bytes32 private constant EMPORIUM_SIGNATURE_TYPEHASH =
        keccak256(
            "EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)EmporiumOperation(address endpoint,bool invokeWallet,uint128 value,bytes callData)"
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L216-244)
```text
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
