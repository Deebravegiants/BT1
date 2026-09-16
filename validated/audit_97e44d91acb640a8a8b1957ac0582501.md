Based on the investigation, I found a genuine analog: the `FillOptions.validUntil` mechanism in `IntentGatewayV2.fillOrder` was specifically built to prevent a solver's quoted price from being executed after too much time has passed, protecting the solver from price risk — but it measures elapsed time using **destination-chain block numbers**, not wall-clock time, exactly the same class of flaw as the Arcadia auction: a real-world-time-denominated risk window is enforced using an on-chain counter that assumes a steady liveness cadence, and an L2 sequencer outage breaks that assumption in the direction that defeats the protection.

### Title
Solver bid staleness protection (`FillOptions.validUntil`) is measured in L2 block numbers, so a sequencer outage silently extends the real-world price-risk window it exists to bound - (File: `evm/src/apps/IntentGatewayV2.sol`)

### Summary
`fillOrder` enforces `options.validUntil` as a hard bound, in destination-chain block numbers, on how long a solver's signed quote stays executable: `if (options.validUntil != 0 && blockNumber > options.validUntil) revert FillExpired();` [1](#0-0) . Off-chain, this bound is deliberately configured and reasoned about in wall-clock seconds (`bidValiditySeconds`, default 300s) and only converted to a block count at the edge using the chain's *nominal* block time, explicitly because "the risk is in" real time, not blocks [2](#0-1) . The stated purpose is to stop the order placer from holding a "written option" and executing a stale bid once market rates have moved against the solver [3](#0-2) .

### Finding Description
The contract-side check is denominated in `_blockNumber()` purely because it must share a clock with `order.deadline` [4](#0-3) , not because blocks are a good proxy for elapsed time. The conversion from the intended real-time window to a block count assumes blocks accrue at a roughly constant nominal rate [5](#0-4) . When an L2 sequencer stalls (the same class of liveness failure the external report is about), block production halts or stutters while real time keeps passing. A `validUntil` block ceiling computed before the outage does not "expire" while the sequencer is down — it is purely a function of block height, which is frozen — so the solver's quote remains executable at the pre-outage price for the entire real-world duration of the outage plus whatever time it takes the chain to catch up to that block height afterward. This is structurally identical to the reported bug class: a mechanism meant to cap price risk to a bounded real-world window is expressed in a unit (blocks / on-chain height) that silently decouples from wall-clock time exactly when the sequencer misbehaves, so the protection is defeated precisely during the event it should matter most for.

### Impact Explanation
The order placer (who controls the timing of `fillOrder` and holds the session key) can withhold execution of a signed solver bid through a sequencer outage and execute it the moment the sequencer resumes, at a quote that is now stale by the full outage duration rather than the intended ~5 minutes. This reinstates exactly the "free option" the `validUntil` field was added to eliminate [6](#0-5) , forcing the solver to deliver output tokens at a rate that no longer reflects the market, a direct funds-loss vector for the solver/filler, analogous to the "unfair liquidation price / bad debt" impact in the reference report, just on the solver side of an intent fill instead of a lending liquidation.

### Likelihood Explanation
Arbitrum, Optimism, Base and other Hyperbridge-supported L2s have all experienced multi-minute to multi-hour sequencer outages historically (the same precedent cited in the source report). `bidValiditySeconds` defaults to only 300 seconds specifically to keep the option value small under normal conditions [7](#0-6) , so even an outage on the order of tens of minutes to hours (well within observed real-world incidents) multiplies the intended risk window by 10-100x, and no code path re-checks wall-clock time or voids/refreshes in-flight bids when a sequencer resumes.

### Recommendation
Cross-check `validUntil` against a wall-clock timestamp (e.g., derived from an L1 anchor or `block.timestamp` where available) rather than relying solely on destination L2 block count, or explicitly detect/require a minimum inter-block gap tolerance so that a stalled sequencer causes bids to be treated as expired rather than indefinitely valid. At minimum, document and monitor this so fillers can proactively retract exposure ahead of/around known sequencer maintenance windows.

### Proof of Concept
1. A solver signs a bid via the coprocessor with `FillOptions.validUntil = currentBlock + N`, where `N` is computed from `bidValiditySeconds` (300s) using the chain's nominal block time [8](#0-7) .
2. Shortly after the bid is signed, the destination L2's sequencer halts for an extended period (a documented, recurring event class on major L2s).
3. Market price for the swapped assets moves significantly against the solver during the outage.
4. Block height does not advance (or advances only slightly) during the outage, so `blockNumber > options.validUntil` in `fillOrder` never becomes true.
5. Once the sequencer resumes, the order placer calls `select` + `fillOrder` using the still-technically-valid bid [1](#0-0) , forcing the solver to deliver output tokens at the pre-outage rate even though real elapsed time vastly exceeds the intended 300-second protection window.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L443-451)
```text
    function fillOrder(Order calldata order, FillOptions calldata options) public payable nonReentrant {
        uint256 blockNumber = _blockNumber();
        if (order.deadline < blockNumber) revert Expired();
        // The solver's own bound on how long its quoted price stands. Zero means unbounded,
        // which is the right default for a solver filling directly — it is only at risk from
        // its own staleness. It matters for a bid signed through the coprocessor, where the
        // order placer chooses the moment of execution and nothing else caps the wait.
        if (options.validUntil != 0 && blockNumber > options.validUntil) revert FillExpired();
        bytes32 commitment = keccak256(abi.encode(order));
```

**File:** sdk/packages/simplex/docs/ai/changelog/2026-08-27-bids-carry-an-on-chain-expiry-bidvalidityseconds.md (L1-16)
```markdown
# 2026-08-27 — Bids carry an on-chain expiry (`bidValiditySeconds`)

Every bid this filler signs now sets `FillOptions.validUntil`, so `fillOrder` reverts `FillExpired` once the quote
has gone stale. Configured as `simplex.bidValiditySeconds`, default 300 (5 minutes).

A bid is a firm price the order placer takes up whenever they choose, and nothing bounded that window:
`order.deadline` is placer-chosen with no ceiling, and `enqueueRetraction` only clears the bid on Hyperbridge, which
has no effect on the destination chain. A bid signed at one rate stayed executable indefinitely and was exercised only
if the rate moved against us — a written option on this filler's inventory, at no premium. Volatile pairs
(USDC/CNGN) are the worst case, since the naira reprices in steps rather than drifting.

Operators configure seconds because that is the unit the risk is in; the contract compares block numbers, so the
value is converted per destination chain from the chain's nominal block time (`Chain.blockTime`, milliseconds in
viem), with a 30-second discovery allowance added before the conversion and the result rounded up — seconds rather
than a block count, because the lag between reading the head and the fill landing is wall-clock and does not scale
with block time.
```

**File:** sdk/packages/sdk/docs/ai/decisions/2026-08-27-the-bid-expiry-rides-in-filloptions-not-in-the-bid-signature.md (L20-29)
```markdown
The cost is that this fires at execution rather than validation: an expired bid is included, the nonce is consumed
and the account pays that op's gas, where a validation-time range would have had the bundler drop it for free. That
is a bounded, one-off cost per bid — and consuming the nonce permanently retires the bid, which the validation-time
version does not do. Fund loss, the thing that matters, is prevented either way.

Denominated in blocks rather than a timestamp so it reads against the same clock as `order.deadline` (`_blockNumber()`,
the L2 block number where those differ), and so the two cannot disagree about what "expired" means.

`0` means unbounded. That is the right default for a solver filling directly — it is only exposed to its own
staleness — and it keeps every existing caller working. The protection is opt-in by the party that needs it.
```

**File:** sdk/packages/simplex/docs/ai/decisions/2026-08-27-bid-tenor-is-configured-in-seconds-and-written-in-blocks.md (L1-16)
```markdown
# 2026-08-27 — Bid tenor is configured in seconds and written in blocks

Chosen: `bidValiditySeconds` (default 300) is converted to a block height per destination chain in
`ContractInteractionService.bidValidUntilBlock()`.

The on-chain field has to be blocks: `fillOrder` compares it against `_blockNumber()`, the same clock as
`order.deadline`, and having the two disagree about what "expired" means would be a trap. But blocks are the wrong
unit for an operator — 5 minutes is 25 blocks on Ethereum and 150 on Base, so a single configured block count would
mean something different on every chain, and price risk is denominated in time, not blocks. Converting at the edge
keeps both sides in their natural unit. Rounding is deliberately up: erring long costs a slightly stale quote, erring
short silently drops bids we would have won.

300 seconds is chosen to cover the quote-to-fill path and little more: cross-chain confirmation waits reach roughly
180s on the deepest default policies, so 5 minutes clears the mechanical part of the round trip while keeping the
window over which the quoted price is a firm commitment short. On a volatile pair that is the number that matters —
optionality handed to the placer scales with time, and USDC/CNGN reprices in steps rather than drifting.
```

**File:** sdk/packages/sdk/docs/ai/changelog/2026-08-27-filloptions-carries-a-validuntil-and-fillorder-has-two-shapes.md (L16-20)
```markdown
Why the field exists: a solver bidding through the coprocessor signs this calldata and then has no further say in
when it is used. The order's `deadline` is placer-chosen with no ceiling, retracting the bid on Hyperbridge does not
reach the destination chain, and the placer holds the session key — so a signed bid stayed executable indefinitely
and was taken up only once the rate had moved against the solver. `validUntil` rides in the calldata, which
`userOpHash` already covers, so it is tamper-proof without touching the signature format.
```
