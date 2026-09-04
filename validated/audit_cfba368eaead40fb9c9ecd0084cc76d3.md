### Title
Emporium wallet-signature (`EMPORIUM_SIGNATURE_TYPEHASH`) does not bind the fee token or relay address, allowing unauthorised ERC20 debits from a signer's `HinkalWallet` - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
The external report describes a class of bug where a value-affecting event/authorization is emitted/granted for a broader scope than what was actually verified per-item (per-tokenId in the PoolTogether case). The analogous break here is an *authorization* scope mismatch: the EIP-712 signature a wallet owner provides to authorise an Emporium "Stateful Interaction" only commits to the `ops`, `maxFee`, and `deadline`, but the Emporium contract uses unsigned, relay/prover-supplied fields (`feeStructure.feeToken`, `circomData.erc20TokenAddresses`, `circomData.relay`) to decide which ERC20 token and to which address funds are actually pulled from the wallet, up to the numeric `maxFee` cap — this breaks the equality "wallet op executed == wallet op authorised by signer."

### Finding Description
`EmporiumUpgradeable.verifyWallet()` reconstructs and checks an EIP-712 hash using `EMPORIUM_SIGNATURE_TYPEHASH`: [1](#0-0) 

The typed-data struct only covers `message`, `ops`, `maxFee`, and `deadline`: [2](#0-1) 

The only per-fee check performed is `circomData.feeStructure.flatFee > stack.maxFee` — there is no check that binds `feeStructure.feeToken`, `circomData.erc20TokenAddresses`, or `circomData.relay` to anything the wallet owner signed.

When the fee is later charged, `payRelayFees()` iterates `circomData.erc20TokenAddresses` (relay/prover supplied, not part of the wallet's signed hash), and for the stateful-wallet path simply uses `relayFee = flatFee` for whichever token equals `feeStructure.feeToken`: [3](#0-2) 

This flatFee is then pulled directly from the signer's `HinkalWallet` via `sendToRelayFromWallet` → `IHinkalWallet(signerAddress).doSendToRelay(relay, relayFee, feeToken)`: [4](#0-3) 

`HinkalWallet.doSendToRelay` is `onlyEmporium`-gated and executes an unconditional ERC20/ETH transfer out of the wallet with the token/recipient chosen entirely by the Emporium call (i.e., by whoever crafted `circomData`, typically the relay/prover), not by the wallet owner: [5](#0-4) 

Because `feeStructure.feeToken`, `erc20TokenAddresses`, and `relay` are outside both (a) the shielded-note EdDSA `signedMessageHash`/`calldataHash` binding that authenticates the *note owner's* transaction (which is not applicable here, since it's the *wallet owner's* signature that authorises the wallet debit) and (b) the `EMPORIUM_SIGNATURE_TYPEHASH` that authenticates the *wallet owner*, the numeric cap `maxFee` is denomination-agnostic. A relay/prover that controls `circomData` (but not the wallet's private key) can select any ERC20 the wallet holds as `feeStructure.feeToken`, and any `circomData.relay` address, and drain up to `maxFee` *units* of that arbitrary token — which can be worth far more than what the wallet owner intended when signing a numeric `maxFee` (which is normally interpreted relative to a specific gas/fee token in the flow they approved).

### Impact Explanation
This is theft of user (wallet-owner) funds via a wallet operation (`doSendToRelay`) not authorised by the signer as to token denomination or recipient — matching the in-scope category "executing calls or moving assets a wallet owner or prover never authorised" (High/Critical depending on token value extracted, since it is a direct value-bearing debit from the signer's `HinkalWallet` balance to an address chosen by the transaction submitter).

### Likelihood Explanation
Requires a malicious or compromised relay/prover to submit a `circomData`/`EmporiumStack` combination where `feeStructure.feeToken` is set to a high-value ERC20 held in the target `HinkalWallet` (rather than the token the signer intended) and `circomData.relay` set to an attacker-controlled address, with `feeStructure.flatFee` set up to `stack.maxFee`. Since `maxFee` is a bare number with no token binding in the signed struct, this is straightforward for any party constructing the calldata (the relay), and does not require the wallet owner's private key.

### Recommendation
Include `feeStructure.feeToken` (and ideally `circomData.relay`) inside the `EMPORIUM_SIGNATURE_TYPEHASH` payload that the wallet owner signs, so the signature explicitly authorises which token and up to what amount can be debited from the `HinkalWallet`, and to which relay address it may be sent.

### Proof of Concept
1. User signs an Emporium message authorising `ops` with `maxFee = 1000` (intending this to be 1000 units of USDC, a token in their `HinkalWallet`).
2. The relay/prover builds `circomData` for the same `emporiumMessage` but sets `feeStructure.feeToken = WBTC` (also held by the wallet) and `feeStructure.flatFee = 1000`, `circomData.relay = attacker`.
3. `EmporiumUpgradeable.verifyWallet` only checks `1000 <= stack.maxFee (1000)` and the EIP-712 hash (which never referenced feeToken) — signature passes.
4. `payRelayFees` → `payRelay` → `sendToRelayFromWallet` → `HinkalWallet.doSendToRelay` transfers 1000 units of WBTC (not USDC) from the victim's wallet to the attacker-controlled relay address, far exceeding the fee the user believed they authorised.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L36-39)
```text
    bytes32 private constant EMPORIUM_SIGNATURE_TYPEHASH =
        keccak256(
            "EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)EmporiumOperation(address endpoint,bool invokeWallet,uint128 value,bytes callData)"
        );
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L216-237)
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
