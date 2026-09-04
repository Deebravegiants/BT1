Confirmed — nothing in `performHinkalChecks`, `dimensionsCheck`, or `checkOnchainCreation` binds `emporiumMessage` to a specific signer; it's only decoded and compared inside `EmporiumUpgradeable.verifyWallet` itself.

### Title
Unauthenticated front-run of `cancelEmporiumMessage` permanently freezes any victim's pending Emporium action - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`cancelEmporiumMessage` only verifies that the cancellation signature recovers to `msg.sender`, without any check that `msg.sender` matches the `stack.signerAddress` that will later be decoded inside `runAction`/`verifyWallet` for that same `emporiumMessage` id. Since `emporiumMessage` is an arbitrary off-chain-chosen `uint256` with no on-chain binding to a signer at creation time, any unprivileged attacker can sign their own `EmporiumCancel(message)` for the same numeric id and permanently set `usedMessages[emporiumMessage] = true` before the victim's transaction lands.

### Finding Description
The equality that should hold is: `usedMessages[id]` can only be set to `true` by (a) a successful `runAction` executed under the real intended signer of that id, or (b) a cancellation signed by that same intended signer. Instead, `cancelEmporiumMessage` at [1](#0-0)  only checks `recoveredAddress == msg.sender`, with the recovered address derived purely from `EMPORIUM_CANCEL_TYPEHASH = keccak256("EmporiumCancel(uint256 message)")` [2](#0-1) , which binds only the numeric `message` value, not any signer identity tied to that id.

Because `usedMessages` is declared as a flat `mapping(uint256 => bool)` in `EmporiumStorage` with no per-signer namespace [3](#0-2) , and `verifyWallet` checks/sets this same global slot before ever inspecting `stack.signerAddress` [4](#0-3) , an attacker can:
1. Observe or brute-force the victim's chosen `emporiumMessage` id `X` (leaked via mempool/relay queue since it must be embedded in `circomData.emporiumMessage` for the later `transact` call).
2. Sign their own valid `EmporiumCancel(X)` message with their own key, producing `v, r, s` such that `recoveredAddress == msg.sender == attacker`.
3. Call `cancelEmporiumMessage(X, v, r, s)`, which passes the `recoveredAddress == msg.sender` check trivially (attacker always controls both sides) and sets `usedMessages[X] = true` globally.
4. When the victim's `transact`/`runAction` call later executes `verifyWallet(stack, circomData)` with `circomData.emporiumMessage == X`, it hits `if ($.usedMessages[circomData.emporiumMessage]) revert UsedMessage();` and fails permanently.

None of the upstream guards (`performHinkalChecks`, `dimensionsCheck`, `checkOnchainCreation` in `HinkalHelper.sol`) constrain `emporiumMessage` to a signer, and `stack.signerAddress` is only decoded from `circomData.externalActionData.externalActionMetadata` inside `runAction` itself [5](#0-4) , well after the id has already been claimable by anyone via `cancelEmporiumMessage`. The comment on `cancelEmporiumMessage` claims "so no one else can cancel it for them" [6](#0-5) , but this is false: the design never checks that the canceller is the same account that legitimately owns/would-sign that id — it only checks self-consistency of the attacker's own signature against their own address, which is trivially always satisfiable.

### Impact Explanation
Any unprivileged attacker can permanently freeze any victim's pending Emporium external action (any numeric `emporiumMessage` id) with zero cost beyond gas and no private key requirement from the victim. Funds already staged in the Emporium contract in anticipation of that action become stranded pending manual/off-chain recovery, and the intended `externalActionData`/wallet calls never execute. This matches "Critical - permanent freezing of user funds / executing calls or moving assets a wallet owner or prover never authorised" since it denies the wallet owner the authorized action permanently for that id, and is trivially repeatable across every id the attacker can observe or guess.

### Likelihood Explanation
The precondition is simply that the attacker learns the victim's chosen `emporiumMessage` id before it lands on-chain — this is explicitly stated as observable via mempool or relay queue leakage, and IDs are otherwise low-entropy `uint256` values chosen off-chain with no mandatory randomness requirement enforced by the contract. The attack costs one cheap transaction (`cancelEmporiumMessage`) with a self-signed EIP-712 message, requires no special role, and is fully repeatable against every pending id the attacker can front-run.

### Recommendation
Bind the cancellation authority to the actual intended signer of the pending stack rather than to an arbitrary self-signed message. Options: (1) require the canceller to supply the same `EmporiumStack`/`signerAddress` context and check `recoveredAddress == stack.signerAddress` (recovered from the original `EMPORIUM_SIGNATURE_TYPEHASH` cancellation variant) instead of `msg.sender`; or (2) namespace `usedMessages` by `(signerAddress, emporiumMessage)` so cancellation and consumption are scoped per-signer, eliminating any cross-account collision.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, set up `hinkalHelper` mock so `runAction` is reachable via `onlyAllowedRecipient`.
2. Victim off-chain picks `emporiumMessage = X`, signs a valid `EmporiumSignature` stack with `stack.signerAddress = victim`, embeds `X` in `circomData.emporiumMessage`, but has not yet submitted the `transact` tx.
3. Attacker (a separate EOA with its own private key, no relation to victim) signs `EmporiumCancel(X)` with its own key and calls `cancelEmporiumMessage(X, v_a, r_a, s_a)` directly — assert it succeeds and `usedMessages[X] == true` is set (verifiable via a subsequent revert).
4. Simulate the victim's transaction reaching `runAction` with the same `circomData.emporiumMessage = X` and victim's valid stack signature — assert it reverts with `UsedMessage()` despite the attacker never possessing the victim's key, and despite `recoveredAddress` inside `verifyWallet` never being checked/computed because of the early revert.
5. Assert both sides of the equality diverge: expected owner of consumption right for id `X` is `victim` (per `stack.signerAddress`), but actual party who irreversibly consumed `usedMessages[X]` was `attacker`.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L41-42)
```text
    bytes32 private constant EMPORIUM_CANCEL_TYPEHASH =
        keccak256("EmporiumCancel(uint256 message)");
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-90)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external override onlyAllowedRecipient returns (UTXO[] memory) {
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );

        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        verifyWallet(stack, circomData);

```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-316)
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L351-352)
```text
    /// @notice Lets a signer burn `emporiumMessage` before it's used, via a fresh signature
    /// recovering to msg.sender (so no one else can cancel it for them).
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L353-367)
```text
    function cancelEmporiumMessage(uint256 emporiumMessage, uint8 v, bytes32 r, bytes32 s) external {
        EmporiumStorageVars storage $ = _getEmporiumStorage();

        bytes32 hashedMessage = _hashTypedDataV4(
            keccak256(abi.encode(EMPORIUM_CANCEL_TYPEHASH, emporiumMessage))
        );

        (address recoveredAddress, ECDSA.RecoverError err) = ECDSA.tryRecover(hashedMessage, v, r, s);
        bool verified = err == ECDSA.RecoverError.NoError && recoveredAddress == msg.sender;
        if (!verified) {
            revert InvalidSignature();
        }

        $.usedMessages[emporiumMessage] = true;
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumStorage.sol (L8-11)
```text
    struct EmporiumStorageVars {
        IHinkalHelper _hinkalHelper; // Hinkal Helper may change implementation
        mapping(uint256 => bool) usedMessages;
    }
```
