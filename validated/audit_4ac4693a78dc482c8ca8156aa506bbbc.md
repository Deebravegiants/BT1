### Title
Emporium fee signature omits `feeStructure.feeToken`, allowing wallet fee to be charged in an unauthorized, arbitrary token up to the numeric `maxFee` - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.verifyWallet` binds the signer's authorization only to `message`, the hash of `ops`, `maxFee` and `deadline` via `EMPORIUM_SIGNATURE_TYPEHASH`; it never binds `feeStructure.feeToken` (or `erc20TokenAddresses`). `payRelayFees`'s fallback branch (`!foundToken`) then calls `sendToRelayFromWallet` → `IHinkalWallet(signerAddress).doSendToRelay(relay, feeStructure.flatFee, feeStructure.feeToken)` for any `feeToken` the caller supplies, as long as `flatFee <= maxFee` numerically. Since `feeToken` is unconstrained by the signature, a caller can replay/combine a validly-signed `(message, ops, maxFee, deadline)` payload with an arbitrary high-value `feeToken`, draining the wallet of that token up to `flatFee` units even though the signer never approved being charged in that denomination.

### Finding Description
The claimed equality is: *the token/amount the wallet is charged as a relay fee == the token/amount denomination the signer's `maxFee` was meant to bound*. This equality is broken because `maxFee` is a unit-less number checked only via `circomData.feeStructure.flatFee > stack.maxFee` in `verifyWallet`: [1](#0-0) 

while the actual EIP-712 payload that is signed, `EMPORIUM_SIGNATURE_TYPEHASH`, only commits to `message`, `_hashEmporiumOps(ops)`, `maxFee`, and `deadline` — never `feeStructure` or `feeToken`: [2](#0-1) [3](#0-2) 

In `payRelayFees`, if `circomData.erc20TokenAddresses` never contains `feeStructure.feeToken` in a negative-`deltaAmountChanges` slot, `foundToken` stays `false`, and the fallback pays `feeStructure.flatFee` in `feeStructure.feeToken` directly from the signer's wallet, with the only guard being `signerAddress != address(0)`: [4](#0-3) 

`doSendToRelay` on `HinkalWallet` is gated only by `onlyEmporium`, so the Emporium contract itself is fully trusted to pick the correct token/amount — there is no secondary check at the wallet level: [5](#0-4) 

**Exploit flow:** Because `feeToken`, `erc20TokenAddresses`, and `flatFee`'s *currency* are not part of the signed payload, a caller who possesses a validly-signed `(message, ops, maxFee, deadline)` tuple from the wallet owner (e.g., intended for a routine low-value fee in a stablecoin) can construct a new `circomData` for the same signature that (a) omits `feeStructure.feeToken` from `erc20TokenAddresses`, and (b) sets `feeStructure.feeToken` to any token the wallet happens to hold (e.g., WBTC) with `flatFee` set as high as the numeric `maxFee` allows. `runAction` executes the (irrelevant) `ops`, then `payRelayFees`'s fallback drains up to `flatFee` units of the substituted token from the signer's wallet via `doSendToRelay`, regardless of what token/value the signer actually intended to pay in.

Existing guards do not prevent this: `verifyWallet` only checks the ECDSA recovery against the typehash fields it includes and a raw numeric comparison against `maxFee`; there is no per-token cap, no requirement that `feeToken` be among the operation's touched tokens, and no requirement that `flatFee`'s implied value be economically bounded.

### Impact Explanation
This lets an attacker cause the signer's on-chain wallet (`IHinkalWallet`) to send up to `flatFee` units of an attacker-chosen token to the relay address — moving wallet assets in a token/denomination the wallet owner never authorized via their signature. This matches "executing calls or moving assets a wallet owner ... never authorised" (High). Each valid signature can be exploited once (per `emporiumMessage`, since `usedMessages` prevents replay of the same message), but a single captured/valid signature is enough to drain up to `flatFee` units of any token balance the wallet happens to hold, which may be far more valuable than the fee the owner believed they were approving.

### Likelihood Explanation
Preconditions: the attacker needs a validly-signed `EmporiumSignature` (message, ops-hash, maxFee, deadline) for `stack.signerAddress`, which could come from a legitimate flow the wallet owner authorized for a specific low-value fee token; the wallet must hold a balance of some other, more valuable token; and the crafted `circomData.erc20TokenAddresses`/`feeStructure.feeToken` must satisfy `flatFee <= maxFee` (numeric) while `feeToken` is excluded from the touched-token set so `foundToken` is false. Constructing `circomData` (including `erc20TokenAddresses`, `feeStructure`) is entirely attacker-controlled per the threat model, and `runAction` is reachable via `Hinkal.transact()` by any caller routing to the registered Emporium external action.

### Recommendation
Include `feeStructure.feeToken` (and ideally the full `feeStructure`, or at minimum `variableRate`/`feeToken`) in the `EMPORIUM_SIGNATURE_TYPEHASH` digest so that the signer explicitly authorizes the fee token, not just a unit-less numeric cap. Additionally, consider requiring `feeStructure.feeToken` to be present in `erc20TokenAddresses` (or otherwise validated against a token allow-list known to the signer) before allowing the fallback branch to charge the wallet.

### Proof of Concept
Foundry test outline:
1. Deploy `EmporiumUpgradeable`, `HinkalWallet`, mock ERC20 "USDC" and "WBTC".
2. Fund the `HinkalWallet` (`signerAddress`) with e.g. 1000 WBTC (18 decimals) and 0 USDC.
3. Have the wallet owner sign an `EmporiumSignature` with `maxFee = 100`, `ops = []` (or benign ops), `deadline` in the future, intending `feeToken = USDC` implicitly (never encoded in the signature).
4. Craft `circomData` with `erc20TokenAddresses` that does **not** include the WBTC address in any negative-`deltaAmountChanges` slot, and `feeStructure = {feeToken: WBTC, flatFee: 100, variableRate: 0}`.
5. Call `runAction` (or `Hinkal.transact` routed to Emporium) with this `circomData` and the same valid signature/`stack`.
6. Assert: `foundToken == false` inside `payRelayFees`, the fallback executes, and `IHinkalWallet(signerAddress).doSendToRelay(relay, 100, WBTC)` is called — asserting the wallet's WBTC balance decreases by 100 units and the relay's WBTC balance increases by 100, while the signer only ever intended/signed a numeric cap of 100 assuming a stablecoin denomination.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L36-39)
```text
    bytes32 private constant EMPORIUM_SIGNATURE_TYPEHASH =
        keccak256(
            "EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)EmporiumOperation(address endpoint,bool invokeWallet,uint128 value,bytes callData)"
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L201-259)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L342-349)
```text
        if (block.timestamp > stack.deadline) {
            revert SignatureExpired();
        }

        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
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
