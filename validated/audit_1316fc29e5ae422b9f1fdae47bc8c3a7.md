### Title
Emporium `EmporiumSignature` typed-data omits `feeToken`, allowing relay fee to be charged against an unauthorised, more valuable token from the signer's wallet - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
The `EmporiumUpgradeable` contract lets a `HinkalWallet` owner pre-authorize a batch of operations plus a relay fee cap (`maxFee`) via an EIP-712 signature (`EmporiumSignature`). The signed struct binds only a bare numeric `maxFee`, never the ERC-20 token that fee will be charged in. The actual token used, `circomData.feeStructure.feeToken`, is supplied later by whoever assembles the `CircomData` (the relay/dapp) and is unchecked against the signature. This mirrors the reported class of bug where a signer authorizes a value without the wallet/dapp binding all the relevant context (here: token identity) needed to know what that value really means.

### Finding Description
`EMPORIUM_SIGNATURE_TYPEHASH` only commits to `message`, the hash of `ops`, `maxFee`, and `deadline`: [1](#0-0) 

`verifyWallet` recovers the signer from this hash and only enforces: [2](#0-1) 

Note the check `circomData.feeStructure.flatFee > stack.maxFee` is a raw `uint256` comparison with no token/decimals context, and `circomData.feeStructure.feeToken` never appears in the signed payload.

`payRelayFees` then uses `circomData.feeStructure.feeToken` — attacker/relay-controlled at proof-assembly time — to actually move funds out of the signer's `HinkalWallet`: [3](#0-2) 

`sendToRelayFromWallet` calls the wallet directly (no owner-signed allowance check on the token), which is only gated by `onlyEmporium`: [4](#0-3) [5](#0-4) 

`doSendToRelay` unconditionally forwards to `sendToRelay`, which performs a raw `transferERC20TokenOrETH` for whatever `erc20TokenAddress` is passed in: [6](#0-5) 

Because `feeToken` is outside the signed EIP-712 struct, the equality the protocol should guarantee — "the signer authorized moving at most `maxFee` value out of their wallet" — is broken: the signer only bounds a *unitless number*, while the party constructing `circomData` (a relay or dapp integrating with Emporium) freely selects which token that number is denominated in. `CircomDataBuilder`'s `calldataHash`/SNARK public-input binding constrains the *token holder of the shielded proof* (the prover), not the `HinkalWallet` owner who signs the separate `EmporiumSignature` — these are two distinct authorizing parties, and the wallet-owner's authorization is the one left unbound.

### Impact Explanation
This allows unauthorised movement of assets from a signer's `HinkalWallet` beyond what they intended: a signer who signs `maxFee = N` expecting it to apply to a low-decimal/low-value token (e.g., USDC) can have the same numeric cap applied to a high-decimal/high-value token (e.g., WBTC or WETH) they also hold in the same wallet, since `feeToken` is never checked against the signature. This is "executing calls or moving assets a wallet owner ... never authorised" against relay/protocol fee payment logic, matching the High severity bucket.

### Likelihood Explanation
Any relay or integrating dapp that collects an `EmporiumSignature` from a user can independently choose `feeToken` when assembling the final `CircomData`/transaction, since nothing on-chain re-derives or checks it from the signature. No admin/owner keys or race conditions are needed — a malicious or compromised relay simply picks a different `feeToken` than the one implied by the UI/dapp context when it built the `EmporiumOperation[]` the user reviewed.

### Recommendation
Include `feeStructure.feeToken` (and ideally `feeStructure.variableRate`) in `EMPORIUM_SIGNATURE_TYPEHASH` so the signer's EIP-712 signature binds the exact token and rate the `maxFee` cap applies to, not just a bare number. Re-derive/verify this bound value inside `verifyWallet` before `payRelayFees` is allowed to move funds from the signer's wallet.

### Proof of Concept
1. Alice owns a `HinkalWallet` holding both `USDC` and `WETH`.
2. She reviews an Emporium operation batch in a dapp UI that implies the relay fee will be paid in `USDC`, and signs `EmporiumSignature(message, ops, maxFee=5_000000, deadline)` (intending "5 USDC").
3. A malicious/compromised relay assembles the on-chain `CircomData` with `feeStructure = { feeToken: WETH, flatFee: 5_000000, variableRate: ... }` and the same `ops`/`message`/`deadline`.
4. `verifyWallet` (contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:302-349) only checks `flatFee(5_000000) <= maxFee(5_000000)` — passes — and recovers Alice's valid signature since `feeToken` was never part of the signed hash.
5. `payRelayFees` → `sendToRelayFromWallet` → `HinkalWallet.doSendToRelay` transfers `5_000000` wei of WETH (≈0.005 WETH, dramatically more valuable than 5 USDC) from Alice's wallet to the relay, without her having authorized that token or value.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L223-244)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L342-348)
```text
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
