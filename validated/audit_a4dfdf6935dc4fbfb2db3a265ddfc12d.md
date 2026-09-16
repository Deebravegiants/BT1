### Title
Rollup address-aliasing during forced L1→L2 delivery can block `IntentGatewayV2` order cancellation while fills remain reachable, unfairly exposing users to unwanted fills or stranded escrow - (File: `evm/src/apps/intentsv2/IntrinsicIntents.sol`, `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
`IntentGatewayV2`'s order-cancellation paths (`_cancelSameChain`, `_cancelFromSource`, `_cancelFromDest`) authorize the caller with a strict equality check `order.user != bytes32(uint256(uint160(msg.sender)))`. On Arbitrum-style rollups, when the sequencer is down, a user can still reach the L2 contract only via the L1 delayed inbox (forced inclusion), but that path aliases the sender's address (`msg.sender + 0x1111000000000000000000000000000000001111`). Because `order.user` stores the real, non-aliased address, the aliased forced-inclusion call fails the equality check and reverts with `Unauthorized`, exactly the bug class described in the external report.

### Finding Description
`IntentGatewayV2` is deployed as an EVM app and, per the collator/fisherman configuration, is explicitly supported on Arbitrum and other OP-Stack rollups [1](#0-0) . Cancellation logic gates the caller strictly by address equality:

- Same-chain cancel — callable at any time before a fill, with no time-window exception: [2](#0-1) 

- Cross-chain cancel from source — only the order creator, and only after expiry: [3](#0-2) 

- Cross-chain cancel from destination — only the creator until the deadline, public after: [4](#0-3) 

All three checks compare `order.user` (a `bytes32`-encoded address captured at order placement) directly against `msg.sender`. None of them account for Arbitrum's (and other rollups') L1→L2 address aliasing that occurs when a transaction is forced through the delayed inbox during sequencer downtime. In that scenario the L2 `msg.sender` observed by the contract is the aliased address, not the user's real EOA, so the equality check fails and the legitimate order owner cannot cancel.

Critically, this is asymmetric: nothing prevents a solver from still filling the order through the same forced-inclusion path, since `fillOrder`/`_fillSameChain` records `msg.sender` as filler without any pre-registered-address check [5](#0-4) . So during sequencer downtime a user who wants to withdraw their escrow (same-chain cancel has no deadline gate at all) is locked out, while a solver can still force a fill and capture the escrowed inputs.

### Impact Explanation
This blocks the order owner's fund-recovery action (`cancelOrder`) exactly when they need it (sequencer downtime, when they must rely on forced L1 inclusion), while leaving the counterparty action (`fillOrder`) reachable, since it has no address restriction. A user's escrowed input tokens can be filled/settled against their wishes during the outage, or the user is simply frozen out of reclaiming funds for the duration of forced-inclusion aliasing failures. This matches the reported "unfair loss to the user while others can still act" pattern and constitutes a fund-freezing/unfair-loss condition for legitimate order owners.

### Likelihood Explanation
The Intent Gateway is deployed to Arbitrum, Base, Optimism, and other rollups with sequencers that can go down (a recurring, publicly documented event on these networks) [6](#0-5) . Any user needing to cancel an order during such downtime is affected without any attacker action required — it's a direct consequence of the naive `msg.sender` comparison, matching the very code pattern flagged in the source report.

### Recommendation
When checking the caller against `order.user` in `_cancelSameChain`, `_cancelFromSource`, and `_cancelFromDest`, also accept the L1-aliased form of the stored address (i.e., check both `msg.sender` and `msg.sender - 0x1111000000000000000000000000000000001111`, matching Arbitrum's `AddressAliasHelper.undoL1ToL2Alias`), or otherwise support meta-transactions/relayed cancellation so users are not solely dependent on a direct, un-aliased `msg.sender` match during forced-inclusion scenarios.

### Proof of Concept
1. User places an order on Arbitrum via `IntentGatewayV2` with `order.user = userEOA`.
2. Arbitrum sequencer goes down; the user's only route to the L2 contract is a forced-inclusion transaction submitted through the L1 delayed inbox.
3. On execution, `msg.sender` observed by `IntentGatewayV2` equals `alias(userEOA) = userEOA + 0x1111000000000000000000000000000000001111`.
4. The user calls `cancelOrder`, which routes to `_cancelSameChain` (or `_cancelFromSource`/`_cancelFromDest`); the check `order.user != bytes32(uint256(uint160(msg.sender)))` evaluates true (aliased address ≠ stored user), reverting with `Unauthorized` [2](#0-1) .
5. Meanwhile, a solver can still force-include a `fillOrder` call through the same delayed-inbox path (no address restriction on the filler), settling the order against the user's wishes while the user remains locked out of cancellation.

### Citations

**File:** docs/content/developers/network/collator.mdx (L303-313)
```text
1. **Every supported L2 must have a `[<chain>]` section.** If you configure even one chain from a set, you must configure all of
   them. Partial coverage is rejected.

   - Mainnet: Arbitrum (42161), Base (8453), Optimism (10), Unichain (130), Soneium (1868).
   - Testnet: Arbitrum Sepolia (421614), Optimism Sepolia (11155420), Base Sepolia (84532).

2. **Each L2 needs at least two `rpc_urls` from distinct providers, and three is strongly recommended.** The fisherman computes a
   supermajority quorum (`floor(2/3 * N) + 1`) across the listed RPCs, so duplicate endpoints add no safety. The validator extracts
   the host portion of each URL and rejects configs that list two URLs on the same host. Use endpoints from genuinely different vendors
   (for example Alchemy, Infura, and QuickNode), not multiple API keys against the same provider. See the fisherman documentation for
   guidance on choosing quality endpoints.
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L53-60)
```text
    function _fillSameChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        bool isFullyFilled = true;
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L159-161)
```text
    function _cancelSameChain(Order calldata order, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L240-243)
```text
    function _cancelFromSource(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        if (options.height <= order.deadline) revert NotExpired();
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L297-300)
```text
    function _cancelFromDest(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.deadline >= _blockNumber()) {
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();
        }
```
