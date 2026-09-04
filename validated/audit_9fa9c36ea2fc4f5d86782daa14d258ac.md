### Title
Relay fee token and recipient are excluded from the EIP-712 signature, allowing fee/token substitution theft from the signer's wallet - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`verifyWallet` binds the wallet owner's signature only to `(emporiumMessage, hash(ops), maxFee, deadline)`, leaving `circomData.feeStructure.feeToken`, `circomData.relay`, `circomData.erc20TokenAddresses` and `deltaAmountChanges` completely unconstrained by the signature. Since `payRelayFees`/`payRelay`/`sendToRelayFromWallet` use these unsigned fields to decide which ERC20 token is pulled from the signer's `HinkalWallet` and which address receives it, anyone who obtains a previously-signed `EmporiumStack` payload (public in calldata before/while pending) can resubmit it with a different `feeToken` and `relay`, redirecting payment to themselves and, more critically, denominating the payout in an arbitrary (potentially far more valuable) token still bounded only by the numeric `maxFee` cap that was meant to apply to a specific token.

### Finding Description
The broken equality: `(feeStructure.feeToken, relay) signed by owner == (feeStructure.feeToken, relay) executed`. Tracing `EMPORIUM_SIGNATURE_TYPEHASH` and `_hashEmporiumOps`: [1](#0-0) 

shows the hashed struct only covers `message`, `ops`, `maxFee`, `deadline`. `verifyWallet` reconstructs exactly this hash and only additionally checks `feeStructure.flatFee > stack.maxFee`: [2](#0-1) 

Neither `feeStructure.feeToken` nor `circomData.relay` (nor `erc20TokenAddresses`/`deltaAmountChanges`) appear anywhere in the signed digest. Yet these exact fields are used immediately afterward to move funds out of the signer's smart wallet: [3](#0-2) [4](#0-3) 

The `maxFee` check (`feeStructure.flatFee > stack.maxFee`) is a pure numeric comparison with no unit/currency binding — because `feeToken` isn't signed, the owner's intended cap (e.g. "10 units of USDC") can be reinterpreted as "10 units of WETH" or any other ERC20 the `HinkalWallet` holds, since `doSendToRelay(relay, relayFee, feeToken)` will transfer whatever `feeToken` address is supplied. Likewise `circomData.relay`, the payout recipient, is fully attacker-chosen.

Exploit flow: attacker observes/obtains a signed `EmporiumStack` (signature, `ops` hash inputs, `maxFee`, `deadline`) for a legitimate withdrawal — this data must be visible in calldata for any onchain use, so it is not privileged information. Attacker re-encodes a new `CircomData.externalActionData.externalActionMetadata` containing the identical `stack` (same `ops`, same `v/r/s`) but sets `feeStructure.feeToken` to a high-value token the `HinkalWallet` holds and `feeStructure.flatFee` numerically ≤ `stack.maxFee`, and sets `circomData.relay` to their own address. Attacker calls `Hinkal.transact` → `EmporiumUpgradeable.runAction` → `verifyWallet` (passes, since signature, ops-hash, maxFee, deadline all still match) → `payRelayFees` → `payRelay` → `sendToRelayFromWallet` → `IHinkalWallet(signerAddress).doSendToRelay(attackerRelay, flatFee, expensiveToken)`, draining up to `maxFee` units of the substituted token to the attacker.

None of the existing guards catch this: `verifyWallet`'s signature check validates only the hashed fields that exclude `feeToken`/`relay`; there is no separate onchain check binding `feeStructure.feeToken` or `circomData.relay` to values the signer approved.

### Impact Explanation
An attacker who intercepts a signed `EmporiumStack` payload can redirect the relay-fee payout to an address they control and — because `feeToken` is unconstrained by the signature while `maxFee` is a bare numeric cap — can select an arbitrary, more valuable ERC20 token held by the victim's `HinkalWallet`, extracting up to `maxFee` units of that token instead of the token the signer actually intended. This is direct theft of user funds from the signer's smart-contract wallet to an attacker-controlled address, repeatable for every signed message the attacker can observe before it is consumed (`usedMessages` only prevents replay of the *same* message, not front-running with substituted fee fields). This matches the Critical category ("direct theft of ... user funds").

### Likelihood Explanation
Preconditions: a `stack.signerAddress != address(0)` wallet must have produced (or be about to broadcast) a valid `EmporiumSignature`; the corresponding `emporiumMessage` must not yet be marked used; the attacker needs visibility of the pending transaction's calldata (public once broadcast, standard mempool assumption, not a privileged relay/RPC). Attacker cost is only gas plus front-running priority to land their transaction before the legitimate one (which would otherwise mark `usedMessages[emporiumMessage] = true` first and cause the attacker's copy to revert with `UsedMessage`). This is feasible with standard MEV front-running and does not require any privileged role, matching the "unprivileged attacker" threat model in scope.

### Recommendation
Include `feeStructure.feeToken`, `feeStructure.flatFee`, `feeStructure.variableRate`, and `relay` (or a restricted/whitelisted-relay assertion) in the `EMPORIUM_SIGNATURE_TYPEHASH` digest so the signer explicitly authorizes the exact token and recipient of the relay fee, not just a numeric cap. At minimum, bind `maxFee` to a specific `feeToken` inside the signed struct, and require `circomData.relay` to match a value the signer approved (or restrict it to an address enforced by `RelayStore`/`performHinkalChecks`).

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, a `HinkalWallet` for `signer`, fund the wallet with two ERC20 tokens: `cheapToken` (intended fee token) and `expensiveToken`.
2. Have `signer` sign an `EmporiumStack{ops, maxFee=10, deadline}` via EIP-712 (`EMPORIUM_SIGNATURE_TYPEHASH`).
3. Build `circomDataA` with `feeStructure = {feeToken: cheapToken, flatFee: 10}`, `relay = legitRelay`; build `circomDataB` reusing the identical `stack` (same `v,r,s`, same `ops`) but `feeStructure = {feeToken: expensiveToken, flatFee: 10}`, `relay = attackerRelay`.
4. Call `runAction(circomDataB, deltaAmountChanges)` first (simulating front-run) — assert it succeeds, `verifyWallet` passes (signature/hash check unaffected by `feeToken`/`relay` change), and `attackerRelay` receives 10 units of `expensiveToken` from the `HinkalWallet`.
5. Assert the equality-under-test: `(feeStructure.feeToken, relay)` used in step 3's signature (`cheapToken`, `legitRelay`) != `(feeStructure.feeToken, relay)` actually executed (`expensiveToken`, `attackerRelay`), while `verifyWallet`'s `AUTHORITY`/signature check still returns `verified == true` for both, proving the divergence is unconstrained by the EIP-712 hash.
6. Attempt to replay `circomDataA` afterward and confirm it now reverts with `UsedMessage`, confirming the legitimate relay is permanently locked out and funds already left via the substituted token/recipient.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L201-260)
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
