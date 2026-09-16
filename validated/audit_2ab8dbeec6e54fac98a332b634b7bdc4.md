### Title
`BandwidthManager.purchase()` has no maximum-price guard, letting a legitimate mid-flight tier-price change silently overcharge the buyer - (File: `evm/src/apps/BandwidthManager.sol`)

### Summary
`BandwidthManager.purchase()` computes the fee-token cost from the *current* `tierPrice[tier]` at execution time and immediately pulls that amount from the caller, with no parameter letting the caller cap the price they are willing to pay. [1](#0-0)  This is structurally the same root cause as the referenced 88mph report: an on-chain function returns/consumes a variable, market-controlled quantity (there, interest; here, fee-token cost) computed at execution time, with no caller-supplied bound to guarantee the outcome is still acceptable when the transaction lands.

### Finding Description
`purchase()` reads `tierPrice[tier]`, scales it to the local fee token's decimals, and transfers `amount` from `msg.sender` — all inside a single call, with the price sourced live from storage: [2](#0-1) 

Tier prices are not static: governance pushes price updates to every manager at any time via `dispatch_set_tiers` → `SetTiers`, and `onAccept` overwrites `tierPrice[tier]` unconditionally: [3](#0-2) 

A buyer's frontend calls `quote()`/`tierPrice()` to compute the amount to approve, then submits `purchase()` in a separate transaction. [4](#0-3)  Between the quote and the mined `purchase()` transaction, a price update can land (ordinary governance operation, mempool reordering, or same-block ordering), and `purchase()` will happily charge whatever `tierPrice[tier]` is at execution time — there is no `maxAmount`/`maxPrice18d` parameter and no `require(amount <= maxAmount)` check to abort the purchase if the price has moved unfavorably. The caller's only recourse, exactly as in the original report, is to have already paid (the ERC-20 transfer already executed) before they can react, and there is no mechanism to reclaim the difference or cancel atomically.

### Impact Explanation
A buyer can be charged more than the price they intended to pay for tier bandwidth, with no way to bound the transaction to the quoted price. Because `purchase()` also allows `months` to be a large multiplier and the price update applies globally per chain, the magnitude of overcharge scales with `total18d = price18d * months`, and buyers who pre-approve a large allowance (a common UX pattern to avoid multiple approvals) are exposed to being charged up to their full allowance at an updated (higher) price on any subsequent purchase call, not just the first. This is a direct loss-of-funds vector for bandwidth buyers, matching Medium severity for "unbacked" economic exposure without any bound.

### Likelihood Explanation
Price changes are a documented, expected, non-malicious governance operation (`dispatch_set_tiers`), and the purchasing flow explicitly separates quoting from execution across two transactions/steps. [5](#0-4)  Any buyer submitting a purchase around a scheduled or ad hoc price update — or simply experiencing normal transaction-inclusion delay — is exposed without any malicious actor being required; it only takes an ordinary state change between quote and inclusion, exactly the "long term" concern flagged in the original report.

### Recommendation
- Short term: add a `maxAmount` (or `maxPrice18d`) parameter to `purchase()` and revert if the computed `amount` (or `total18d`) exceeds it, mirroring the report's `minInterestAmount` pattern:
```solidity
function purchase(bytes calldata app, uint256 tier, uint256 months, bytes calldata chain, uint256 maxAmount)
    external
    returns (bytes32 commitment)
{
    ...
    uint256 amount = total18d / scale;
    require(amount <= maxAmount, "BandwidthManager: price exceeded maxAmount");
    ...
}
```
- Long term: ensure every function where a caller pays an amount computed from mutable on-chain state (prices, rates, quotas) exposes a caller-supplied bound so state changes outside the caller's control (governance updates, front-running, or simple inclusion delay) cannot silently produce an unacceptable outcome.

### Proof of Concept
1. Buyer calls `tierPrice(tier)` off-chain / via `quote()` and computes `cost` for `months` months, then approves the manager for `cost`. [6](#0-5) 
2. Before the buyer's `purchase()` transaction is mined, governance dispatches `SetTiers` raising `tierPrice[tier]` (a normal operational action). The manager's `onAccept` writes the new price unconditionally.
3. Buyer's `purchase(app, tier, months, chain)` executes; it reads the now-higher `tierPrice[tier]`, computes a larger `amount`, and calls `safeTransferFrom(msg.sender, address(this), amount)` — succeeding as long as the buyer's pre-approved allowance covers it (common when buyers approve generously to avoid re-approving for multi-month purchases). [7](#0-6) 
4. The buyer is charged the new, higher price with no revert and no way the transaction could have enforced the originally quoted price, since `purchase()` never accepted a price ceiling from the caller.

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

**File:** docs/content/developers/evm/bandwidth/configuration.mdx (L84-99)
```text
## Step 5 — Push tier prices to the manager

```rust
BandwidthPallet::dispatch_set_tiers(
    RawOrigin::Root.into(),
    StateMachine::Evm(8453),
    vec![
        (TierIndex::TierOne,   U256::from(50e18 as u128)),
        (TierIndex::TierTwo,   U256::from(200e18 as u128)),
        (TierIndex::TierThree, U256::from(500e18 as u128)),
        (TierIndex::TierFour,  U256::from(2_000e18 as u128)),
    ],
);
```

This dispatches a `SetTiers` message to the registered manager on `target`. The manager's `onAccept` writes `tierPrice[tier] = price18d` for each row and emits `TierSet(tier, price18d)`. Tiers not in the batch are left untouched.
```

**File:** docs/content/developers/evm/bandwidth/purchasing.mdx (L93-101)
```text

    /// Quote the fee-token cost of a `(tier, months)` purchase.
    function quote(uint256 tier, uint256 months) public view returns (uint256) {
        uint256 price18d = manager.tierPrice(tier);
        uint256 total18d = price18d * months;
        address feeToken = IDispatcher(host).feeToken();
        uint8 dec = IERC20Metadata(feeToken).decimals();
        return total18d / (10 ** (18 - dec));
    }
```

**File:** docs/content/developers/evm/bandwidth/purchasing.mdx (L129-162)
```text
async function purchaseBandwidth() {
  const account = privateKeyToAccount("0xYOUR_KEY")
  const publicClient = createPublicClient({ transport: http("YOUR_RPC") })
  const walletClient = createWalletClient({ account, transport: http("YOUR_RPC") })

  // 1. Quote the cost.
  const tier = 1n
  const months = 3n
  const price18d = await publicClient.readContract({
    address: MANAGER, abi: managerAbi, functionName: "tierPrice", args: [tier],
  })
  const feeToken = await publicClient.readContract({
    address: HOST, abi: hostAbi, functionName: "feeToken",
  })
  const dec = await publicClient.readContract({
    address: feeToken, abi: erc20Abi, functionName: "decimals",
  })
  const total18d = price18d * months
  const cost = total18d / 10n ** (18n - BigInt(dec))

  // 2. Approve the manager.
  await walletClient.writeContract({
    address: feeToken, abi: erc20Abi, functionName: "approve",
    args: [MANAGER, cost],
  })

  // 3. Buy. `chain` is the UTF-8 string of the credit chain id.
  const app   = encodePacked(["address"], [APP])
  const chain = new TextEncoder().encode("EVM-8453")  // Base

  const txHash = await walletClient.writeContract({
    address: MANAGER, abi: managerAbi, functionName: "purchase",
    args: [app, tier, months, chain],
  })
```
