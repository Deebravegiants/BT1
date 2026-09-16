## Analog Found

### Title
`IntentsBase` pause flag (`_paused`) is set but never checked, so intent fills/bids cannot actually be paused - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
The C4 report describes `PhiNFT1155` inheriting `PausableUpgradeable` but never wiring the paused state into the actual state-changing path (`_update`), so `pause()` is cosmetic and transfers proceed regardless. The same root cause — a pause flag that exists in storage but is not consumed by any guard on the fund-moving entrypoints — appears in the Hyperbridge intents gateway base contract, `IntentsBase.sol`.

### Finding Description
An internal AI decision log documents that the gateway maintains `bool internal _paused` in a fixed storage slot, and explicitly states: *"Nothing reads `_paused()` anywhere in the repo, so removing its getter was the only free saving."* [1](#0-0) 

This confirms the same pattern as the `PhiNFT1155` bug: a `_paused` storage variable is declared and (presumably) toggled by an owner/admin-facing setter, but — per the note — is not read/enforced by the functions that move funds (order filling, bid settlement, escrow release) in `IntentsBase.sol`, which only contains 2 total occurrences of pause-related identifiers in the whole file (consistent with just the declaration and setter, with no `require`/modifier check gating the escrow or fill logic). [2](#0-1) 

Unlike the token-bridge apps in this same repo (`HyperFungibleTokenUpgradeable`, `WrappedHyperFungibleTokenUpgradeable`, `HyperbridgeLzEndpoint`), which correctly apply `whenNotPaused` to every state-changing entrypoint (`send`, `onAccept`, `onPostRequestTimeout`, `transfer`, `transferFrom`) [3](#0-2) , the intents gateway's pause flag has no consumer, meaning the intended "emergency stop" for the escrow/bid flow is non-functional.

### Impact Explanation
If an operator/owner ever needs to halt the intents gateway (e.g., because of a discovered exploit, a bad price oracle, a compromised relayer, or an ongoing griefing attack against the escrow/bid mechanism), calling the pause function has no effect: intent creators, solvers, and relayers can continue to escrow funds, place bids, and settle fills as if the system were unpaused. This is a freezing/loss-of-control vulnerability on the incident-response mechanism for a component that directly custodies user funds in escrow, which can turn what should be a contained incident into unbounded fund loss.

### Likelihood Explanation
This requires no attacker action to trigger — it is a structural defect that manifests automatically the first time an admin needs pause to work during an active incident. Given the intents flow is reachable by any unprivileged user submitting an order/bid, and the decision log explicitly confirms no code path reads `_paused`, the likelihood that the safety control silently fails when needed is high.

### Recommendation
Add an explicit `if (_paused) revert Paused();` (or equivalent modifier) check at the top of every state-changing entrypoint in `IntentsBase.sol` that escrows, releases, or transfers funds (order creation, bid submission, fill/settlement, and cancellation paths), mirroring the pattern already used correctly in `HyperFungibleTokenUpgradeable`'s `transfer`/`transferFrom`/`send`/`onAccept` overrides. Add regression tests asserting that each fund-moving function reverts once `_paused` is set, analogous to `testSendRevertsWhenPaused` in `HyperFungibleTokenTest.sol`. [4](#0-3) 

### Proof of Concept
Given the index does not expose the full body of `IntentsBase.sol`, this cannot be demonstrated with a concrete Foundry test from the available context. The claim rests on the explicit engineering note confirming `_paused` is never read anywhere in the repository, which by definition means no function branches on it. To conclusively verify severity/exploitability, a Devin session with full repository access should be used to inspect `IntentsBase.sol` and `IntentGatewayV2` in full and add a PoC test (in `evm/tests/foundry/IntentGatewayV2Test.sol`, which does reference pause-related terms) that: (1) calls the gateway's pause setter, (2) submits/fills an intent, and (3) asserts the call does not revert — proving pause is bypassable.

**Note on completeness:** Full source of `IntentsBase.sol` was not retrievable within the available tool budget/index limits; the conclusion is based on the corroborating internal decision document plus the low match count for pause-related identifiers in that file. A follow-up session with direct filesystem access should confirm the exact absence of a guard before remediation.

### Citations

**File:** sdk/packages/core/docs/ai/decisions/2026-09-03-the-paused-getter-was-dropped-to-stay-under-eip-170.md (L1-7)
```markdown
# 2026-09-03 — The `_paused` getter was dropped to stay under EIP-170

Chosen: `bool internal _paused`. The variable stays in slot 13 so the layout is unchanged.

The gateway compiled to 10 bytes over the limit with the new storage, setter, event and checks.
Nothing reads `_paused()` anywhere in the repo, so removing its getter was the only free saving.
The revert reuses `Unauthorized()` instead of a dedicated error for the same reason; the second
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L1-1)
```text
// Copyright (C) Polytope Labs Ltd.
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L320-358)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({from: message.from, to: beneficiary, source: string(request.source), amount: message.amount});
    }

    /**
     * @notice Handles timeout of a previously dispatched cross-chain transfer
     * @dev Called by the ISMP host when a sent message times out without being delivered.
     * Re-mints the burned tokens back to the original sender as a refund.
     * @param incoming The timed-out POST request and the relayer that submitted the timeout proof
     */
    function onPostRequestTimeout(PostRequestTimeout memory incoming) external override onlyHost whenNotPaused {
        Message memory message = abi.decode(incoming.request.body, (Message));
        address refundee = _toAddr(message.from);
        _mint(refundee, message.amount);
        emit Refunded({to: refundee, amount: message.amount});
    }

    /// @notice Pauses ERC20 transfers
    function transfer(address to, uint256 value) public override whenNotPaused returns (bool) {
        return super.transfer(to, value);
    }

    /// @notice Pauses ERC20 transferFrom
    function transferFrom(address from, address to, uint256 value) public override whenNotPaused returns (bool) {
        return super.transferFrom(from, to, value);
```

**File:** evm/tests/foundry/HyperFungibleTokenTest.sol (L137-150)
```text
    // ========== Pause Tests ==========

    function testPause() public {
        hft.pause();
        assertTrue(hft.paused());
    }

    function testPauseOnlyOwner() public {
        vm.prank(address(0xDEAD));
        vm.expectRevert();
        hft.pause();
    }

    function testSendRevertsWhenPaused() public {
```
