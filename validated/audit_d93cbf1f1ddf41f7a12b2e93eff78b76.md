## Finding

### Title
Missing price-slippage protection in `BandwidthManager.purchase()` allows buyers to be charged a different price than quoted — ([File: evm/src/apps/BandwidthManager.sol])

### Summary
`BandwidthManager.purchase()` charges the caller based on the **live** `tierPrice[tier]` at execution time, with no parameter letting the caller cap the amount they are willing to pay and no deadline. If a caller approves the fee token for a purchase based on an off-chain quote (or holds a standing allowance to the manager, which is the pattern the docs themselves encourage to avoid repeated approvals) and the tier price changes via a governance `SetTiers` update before the transaction lands, the buyer is silently charged the new price instead of the quoted one.

### Finding Description
`purchase()` reads the current price directly from storage and immediately pulls that amount via `safeTransferFrom`, with no upper bound supplied by the caller: [1](#0-0) 

Tier prices are not fixed for the caller — they are mutable storage updated at any time by an inbound `SetTiers` governance message delivered via `onAccept`: [2](#0-1) 

The SDK/docs guide buyers to `quote()` off-chain, then `approve()` the manager for the *exact scaled amount* and call `purchase()`: [3](#0-2) 

There is no `maxCost`/`maxPrice` argument on `purchase()`, and no `deadline`. Because `tierPrice` can be updated by a legitimate `SetTiers` dispatch at any block (there is no epoch/versioning tied to the buyer's quote), any `purchase()` transaction sitting in the mempool — or submitted against a standing/looser allowance than the exact quoted amount — can execute against a new price. The buyer has no on-chain mechanism to guarantee the price they agreed to off-chain is the price actually charged; the only failure mode built in is `ERC20InsufficientAllowance` if the allowance happens to be tight and the price goes up, but any allowance sized above the exact amount (a common integration pattern to reduce approval friction, as with vaults granting "max allowance") silently permits an unbounded overcharge up to the allowance.

This mirrors the reported Arrakis vault issue precisely: a caller-facing function that transfers ERC-20 value determined by a price that can move between quote and execution, with no `amountMax`/slippage bound and no deadline exposed to the caller.

### Impact Explanation
A bandwidth purchaser can lose funds beyond what they intended to pay for a specific tier/months purchase, up to the size of their token allowance to `BandwidthManager`, whenever a tier price increases between the time they quote/approve and the time their `purchase()` transaction is mined. Given the docs' own recommended flow (approve exact quoted amount, but also note only one approval needed for such purchases and possible standing allowances for repeat-buy scenarios), and that purchases are ordinary mempool transactions with no expiry check, this is a realistic loss-of-funds vector for legitimate users, not an admin-only scenario.

### Likelihood Explanation
Price updates are pushed as ordinary governance operations (`SetTiers`) that are expected to occur periodically as fee-token/market conditions change — this is routine protocol operation, not an attack requiring a malicious insider. Any buyer transaction pending at the time of such an update is exposed. The likelihood scales with allowance sizing practices and mempool latency, both of which are common in production integrations.

### Recommendation
Add a caller-supplied `maxCost` (or `maxPrice18d`) parameter to `purchase()` and revert if the computed `amount` (or `total18d`) exceeds it. Optionally add a `deadline` parameter to reject stale transactions. This lets buyers bound their exposure to tier-price changes the same way AMMs bound slippage with `amountOutMin`/`amountInMax`.

### Proof of Concept
1. Buyer calls `tierPrice(tier)` off-chain, computes `amount`, and approves `BandwidthManager` for that `amount` (or a larger standing allowance for future top-ups).
2. Buyer submits `purchase(app, tier, months, chain)`.
3. Before the transaction is mined, governance dispatches a `SetTiers` update raising `tierPrice[tier]`.
4. `onAccept` applies the new price (`evm/src/apps/BandwidthManager.sol` lines 208-219) in an earlier block/transaction.
5. The buyer's pending `purchase()` executes, recomputing `amount` from the new, higher price, and pulls that (higher) amount via `safeTransferFrom` — succeeding silently if the allowance covers it, charging more than the buyer agreed to with no recourse.

### Citations

**File:** evm/src/apps/BandwidthManager.sol (L153-170)
```text
    function purchase(bytes calldata app, uint256 tier, uint256 months, bytes calldata chain)
        external
        returns (bytes32 commitment)
    {
        if (app.length == 0 || app.length > MAX_APP_LENGTH || chain.length == 0 || months == 0) {
            revert InvalidPurchase();
        }
        uint256 price18d = tierPrice[tier];
        if (price18d == 0) revert UnknownTier();

        uint256 total18d = price18d * months;
        address feeToken = IDispatcher(_host).feeToken();
        uint8 dec = IERC20Metadata(feeToken).decimals();
        uint256 scale = 10 ** (18 - dec);
        if (total18d % scale != 0) revert PriceNotRepresentable();
        uint256 amount = total18d / scale;

        IERC20(feeToken).safeTransferFrom(msg.sender, address(this), amount);
```

**File:** evm/src/apps/BandwidthManager.sol (L208-219)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        PostRequest calldata request = incoming.request;

        if (!request.source.equals(IDispatcher(_host).hyperbridge())) revert UnauthorizedAction();

        OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
        if (action == OnAcceptActions.SetTiers) {
            Tier[] memory updates = abi.decode(request.body[1:], (Tier[]));
            for (uint256 i = 0; i < updates.length; i++) {
                tierPrice[updates[i].tier] = updates[i].price;
                emit TierSet(updates[i].tier, updates[i].price);
            }
```

**File:** docs/content/developers/evm/bandwidth/purchasing.mdx (L94-102)
```text
    /// Quote the fee-token cost of a `(tier, months)` purchase.
    function quote(uint256 tier, uint256 months) public view returns (uint256) {
        uint256 price18d = manager.tierPrice(tier);
        uint256 total18d = price18d * months;
        address feeToken = IDispatcher(host).feeToken();
        uint8 dec = IERC20Metadata(feeToken).decimals();
        return total18d / (10 ** (18 - dec));
    }
}
```
