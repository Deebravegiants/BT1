### Title
Emporium `verifyWallet` never binds `relay` or `feeStructure.feeToken` to the EIP‑712 signature, letting a replayed stack pay fees to an unauthorised relay/token - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`verifyWallet` recovers the signer over `(emporiumMessage, opsHash, maxFee, deadline)` only, and separately checks `feeStructure.flatFee <= stack.maxFee`. Nothing in the signed payload constrains `circomData.relay` or `feeStructure.feeToken`, so any caller who can present a validly-signed `EmporiumStack` (e.g. the legitimate relay flow, or a previously-submitted-but-reverted transaction they observed) can resubmit it via `Hinkal.transact` with a different `circomData.relay` and/or `feeStructure.feeToken`, redirecting up to `stack.maxFee` worth of the signer's wallet funds to an attacker-controlled relay address in a token the signer never selected.

### Finding Description
The broken equality is: **(assets leaving the wallet, their destination) == (ops, maxFee) the owner signed.**

`verifyWallet` computes the signed hash strictly from: [1](#0-0) 

and the only fee-related guard is: [2](#0-1) 

Note that `circomData.relay` and `feeStructure.feeToken` are read directly from the attacker-supplied `CircomData` passed into `runAction`/`payRelayFees`, and neither field is part of `EMPORIUM_SIGNATURE_TYPEHASH`: [3](#0-2) 

In `payRelayFees`, when `signerAddress != address(0)` (the signed-wallet path), the relay fee is simply `flatFee` (bounded by `maxFee`), and is sent to `circomData.relay` in `feeStructure.feeToken`, pulled directly out of the signer's wallet contract via `doSendToRelay`: [4](#0-3) [5](#0-4) 

**Attacker's exact call:** obtain (or replay) any validly-signed `EmporiumStack` for a given `emporiumMessage` (still unused per `usedMessages`), then call `Hinkal.transact` targeting Emporium with a `CircomData` whose `feeStructure = {feeToken: <token wallet holds>, flatFee: stack.maxFee, variableRate: 0}` and `relay = <attacker address>`. Because `emporiumMessage`, the ops hash, `maxFee`, and `deadline` are unchanged, `verifyWallet` accepts the signature; `flatFee == maxFee` passes the `<=` check; `payRelayFees` then calls `sendToRelayFromWallet` which invokes `IHinkalWallet(signerAddress).doSendToRelay(relay, flatFee, feeToken)`, transferring `flatFee` of the chosen token from the signer's wallet to the attacker's `relay` address — a destination and token the signer's EIP‑712 signature never specified.

Existing guards do not catch this: `onlyAllowedRecipient` only restricts which contract can call `runAction` (i.e., `Hinkal` itself), not the contents of `circomData`; `usedMessages` prevents replay of the *same* `emporiumMessage` twice but does not prevent the *first* use from being submitted with an unauthorised relay/fee token; the ops-hash check binds only the operations, not the fee-payment side effects.

### Impact Explanation
The signer authorised a numeric fee cap (`maxFee`) for "a relay", trusting the standard flow to route it to the legitimate/whitelisted relay and expected fee token. Because relay address and fee token are outside the signed payload, an unprivileged actor who intercepts/observes any valid signed stack can redirect up to `maxFee` of an arbitrary ERC20 the wallet holds to their own address — theft of relay/protocol fees, and movement of wallet funds to a destination the owner's signature never authorised. This matches the High-severity category: "theft ... of protocol/relay fees" / "executing calls or moving assets a wallet owner or prover never authorised." It is a one-shot theft per captured signature (bounded by `usedMessages`), but each captured/observed valid stack can be independently exploited once, and the amount stolen is limited only by `maxFee` and the wallet's balance of the chosen token.

### Likelihood Explanation
Preconditions: attacker needs access to one previously-issued, still-unused, validly-signed `EmporiumStack` (e.g. visible on-chain before inclusion via mempool, or a relay-submitted request that failed for unrelated reasons and can be resubmitted by anyone since `onlyAllowedRecipient` only gates the calling contract, not who initiates `Hinkal.transact`). No special role is required — the attacker only needs to call `Hinkal.transact` with a crafted `CircomData` and the captured `EmporiumStack` bytes as `externalActionMetadata`. This is feasible and repeatable across any captured signature instance.

### Recommendation
Include `relay` and `feeStructure` (at minimum `feeToken`, and ideally the whole `FeeStructure`) inside the EIP-712 typed data hashed in `verifyWallet` (extend `EMPORIUM_SIGNATURE_TYPEHASH` and the `abi.encode` call), so a signer's authorization is cryptographically bound to the specific relay and fee token/amount, not just an upper-bound numeric cap.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, a mock `IHinkalWallet` holding a test ERC20 balance for `signerAddress`, and a mock `HinkalHelper`.
2. As `signerAddress`, sign an `EmporiumStack` with a trivial no-op `ops` array, `maxFee = X`, `deadline` in the future, using `EMPORIUM_SIGNATURE_TYPEHASH` exactly as the contract computes it.
3. Call `runAction` (simulating `Hinkal.transact`) once with `circomData.relay = relayA`, `feeStructure = {feeToken: tokenA, flatFee: X, variableRate: 0}` — assert `tokenA` balance moved from wallet to `relayA` equals `X`. This is the "legitimate" first use — `usedMessages[emporiumMessage]` becomes `true`.
4. To demonstrate divergence at first use (attacker intercepts before submission): repeat with the *same* signed stack but `circomData.relay = attackerRelay`, `feeStructure.feeToken = tokenB` (a different token the wallet also holds), `flatFee = X`. Assert the call succeeds (signature still verifies since relay/feeToken aren't signed) and `tokenB` balance moves from wallet to `attackerRelay`.
5. Assert both sides of the equality: signed authorization = `(emporiumMessage, opsHash, maxFee=X, deadline)`; actual fund movement = `(tokenB, X, attackerRelay)` — these differ from what the signer intended (no token/relay ever specified), proving the equality `(assets leaving wallet, destination) == (ops, maxFee signed)` is broken.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L346-348)
```text
        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
```
