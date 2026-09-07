# [C] Klever: Marketplace settlement mints KLV when referral % + royalty % exceed the bid (negative seller share silently skipped)

## Summary
Severity: Critical
Advisory: GHSA-p7gw-2pcp-5pf8
CVE: CVE-2026-54754
CWE: CWE-191, CWE-367, CWE-682
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-p7gw-2pcp-5pf8
Type: github-advisory

## Affected
- Go: `github.com/klever-io/klever-go` — affected >=0 <1.7.19

## Details
## Summary

When a marketplace order is settled (`MarketBuy` / `BuyItNow`, and auction `Claim`), the buyer's
payment is split three ways — **referral**, **royalties**, and the **seller (market-order owner)
remainder**:

```
marketOwnerAmount = CurrentBid − referralAmount − royaltiesAmount
```

Referral and royalties are paid out **unconditionally**, but the seller remainder is only paid
**when positive** (`computeMarketOwnerAmount` returns `Ok` and pays nothing when the amount is
`<= 0`). When `referral% + royalty%` exceeds 100% of the bid, `marketOwnerAmount` goes **negative**
and is silently skipped — so the marketplace pays out **more KLV / sale currency than the buyer
paid in**, minting the difference out of thin air.

The combined ceiling `royalty% + referral% <= 100%` **is** checked once, at listing time (`Sell`).
But the two percentages are sourced asymmetrically at settlement:

- **referral %** is **snapshotted** into the order at `Sell` (`MarketOrderData.ReferralPercentage`);
- **royalty %** is **never snapshotted** — it is read **live** from the asset at buy time
  (`asset.Royalties.MarketPercentage`).

So the listing-time invariant is a **time-of-check/time-of-use** guarantee only. After a valid
listing, the asset owner raises the royalty `MarketPercentage` via `AssetTrigger → UpdateRoyalties`;
at the next buy the live royalty plus the snapshotted referral exceed 100%, and the settlement mints
the overflow. The minted funds land in attacker-controlled referral / royalty addresses.

This was **actively exploited on mainnet** (see *Evidence*), minting tens of millions of KLV before
the emergency guard was deployed.

## Affected component

- Repository: `klever-io/klever-go` (node).
- Settlement / mint site: `core/kapp/market/market.go` — `executeBuyMarket` (L575+),
  `computeReferralAmount` (L361+), `computeRoyaltiesAmount` (L490+),
  `computeRoyaltiesFixedDeposit` (L443+), `computeMarketOwnerAmount` (L540+).
- TOCTOU sources: `Sell` combined check (`market.go:908`), order snapshot of referral but **not**
  royalty (`market.go:997`), live royalty mutation via
  `core/kapp/kda/trigger.go` — `handleUpdateRoyaltiesNFTandSFT` (L613+, sets
  `asset.Royalties.MarketPercentage` at L670).
- Reachable from both `Buy` (BuyItNow, `market.go:204+`) and auction `Claim`
  (`market.go:705`, `market.go:731`).
- Pre-fix: **not** gated by any fork flag — exploitable on mainnet. The fix is gated behind the new
  `FixMarketBuyOverflow` activation-epoch flag.

---

## Root cause

### 1. Settlement pays referral + royalty unconditionally, seller remainder only if positive
`core/kapp/market/market.go` — `executeBuyMarket` (L575+):
```go
referralAmount, _  := tools.ComputePercentageI64(marketOrder.CurrentBid,
                          int64(marketOrder.ReferralPercentage), ...)        // L583: SNAPSHOT referral %
royaltiesAmount, _ := tools.ComputePercentageI64(marketOrder.CurrentBid,
                          int64(asset.Royalties.MarketPercentage), ...)      // L587: LIVE royalty %
marketOwnerAmount := marketOrder.CurrentBid - referralAmount - royaltiesAmount  // L591: can go negative

// ---- FIX (FixMarketBuyOverflow), added by the patch ----
if m.forkController.FixMarketBuyOverflow() && marketOwnerAmount < 0 {         // L593-596
    ctx.Receipts().AddError(ctx.ContractID(), common.ErrFieldInvalidRoyalties, common.ErrInvalidValue.Error())
    return transaction.Transaction_AmountInvalid, common.ErrInvalidValue
}

m.computeReferralAmount(ctx, marketOrder, referralAmount, currencyID)   // pays referral in full
m.computeRoyaltiesFixedDeposit(ctx, marketOrder, asset)                 // pays fixed royalty (KLV)
m.computeRoyaltiesAmount(ctx, marketOrder, asset, currencyID, royaltiesAmount) // pays % royalty in full
m.computeMarketOwnerAmount(ctx, marketOrder, currencyID, marketOwnerAmount)    // <-- skips when <= 0
```
`computeMarketOwnerAmount` (L540-542) — the silent skip:
```go
func (m *marketKapp) computeMarketOwnerAmount(... marketOwnerAmount int64) (... , error) {
	if marketOwnerAmount <= 0 {
		return transaction.Transaction_Ok, nil   // negative seller share dropped, NO error
	}
	// ... AddToBalance(marketOwnerAmount) ...
}
```
Meanwhile `computeReferralAmount` (L376) and `computeRoyaltiesAmount` (L515) each `AddToBalance(...)`
the full computed amount with **no matching debit** from the buyer beyond the single
`bidderAcc.SubFromBalance(amount)` taken in `Buy` (`market.go:301`).

**Conservation breaks:** buyer is debited `bid` once; recipients are credited
`referralAmount + royaltiesAmount`. When that sum `> bid`, the surplus
`(referralAmount + royaltiesAmount − bid)` is **minted**.

### 2. The combined ≤100% invariant is enforced only at listing time
`Sell` (`market.go:908`) correctly rejects a listing whose combined cut exceeds 100%:
```go
if asset.Royalties.MarketPercentage + marketplace.ReferralPercentage > core.HundredPercent {
	return transaction.Transaction_ParameterInvalid, common.ErrInvalidValue
}
```
…and snapshots **referral** into the order, but **not** royalty (`market.go:997-998`):
```go
marketOrder := &kapps.MarketOrderData{
	// ...
	ReferralPercentage:    marketplace.ReferralPercentage, // snapshotted
	RoyaltiesFixedDeposit: asset.Royalties.MarketFixed,    // snapshotted
	// NOTE: asset.Royalties.MarketPercentage is NOT snapshotted -> read live at buy
}
```
`MarketOrderData` has no field for the royalty percentage (`kapps/market.pb.go`), so settlement
always re-reads it live from the (mutable) asset.

### 3. Royalty % is mutable after listing
`core/kapp/kda/trigger.go` — `handleUpdateRoyaltiesNFTandSFT` (L613+) lets the asset owner overwrite
`asset.Royalties.MarketPercentage` (L670) with only a **per-field** `<= 100%` check (`CheckValid100Params`,
L651) — it has no knowledge of any outstanding marketplace listing's snapshotted referral. So the
owner can list at, e.g., referral 100% / royalty 0% (sum 100%, passes `Sell`), then raise royalty to
100%, making the buy-time sum 200%.

> The shipped emergency-guard source documents this exact vector:
> *"The royalty percentage is read live at buy time, so a listing made now can be weaponised later
> via UpdateRoyalties."* (`common/emergencyGuard.go`)

**Net effect:** `referralAmount + royaltiesAmount = bid + bid = 2·bid`; `marketOwnerAmount = −bid`
(skipped); **`bid` KLV minted per settlement**, paid to attacker-controlled addresses.

---

## Proof of Concept

### A. Committed regression test (deterministic, runnable today)
`core/kapp/market/market_test.go` — `TestMarketKApp_ExecuteBuyMarket_RoyaltyReferralInflation`.
It builds an order with `ReferralPercentage = 100%` and an asset with `MarketPercentage = 100%`
(the attacker is both the referral and the royalty address), then settles a `bid` of
`25,600,000 KLV` (`25600000000000` base units):

```bash
go test ./core/kapp/market/ -run TestMarketKApp_ExecuteBuyMarket_RoyaltyReferralInflation -v
```

- `FixDisabled_MintsKLVFromThinAir`: settlement returns `Ok`; the attacker address ends with
  `2·bid` credited while only `bid` was paid in — i.e. **`bid` KLV minted**.
- `FixEnabled_RejectsInflation`: with `FixMarketBuyOverflow` on, settlement returns
  `Transaction_AmountInvalid` and the attacker balance stays `0` — **no payout runs**.

### B. End-to-end on a local node (the real attack path)
A single-node local network is sufficient. The exploit is four transactions from one ordinary
funded account; nothing privileged is required.

1. **Create an NFT collection** you own, with `royalties.marketPercentage = 0` and a royalties
   address you control.
2. **Create a marketplace** with `referralPercentage = 10000` (100%) and a referral address you
   control (`CreateMarketplace`).
3. **List** one NFT for sale (`Sell`) on that marketplace. The `Sell` check passes because
   `0 (royalty) + 10000 (referral) = 10000 = HundredPercent`. The order snapshots
   `ReferralPercentage = 10000`.
4. **Raise the royalty** on the asset to 100% (`AssetTrigger / UpdateRoyalties`,
   `marketPercentage = 10000`). Allowed: the per-field check passes and the live combined invariant
   is never re-evaluated against the open listing.
5. **Buy** the listing (`MarketBuy`) from a second account (or settle the auction via `Claim`).
   `referralAmount = bid`, `royaltiesAmount = bid`, `marketOwnerAmount = −bid` (skipped). Your
   referral + royalty addresses receive `2·bid`; the buyer paid `bid`; **`bid` KLV is minted**.

Because the attacker controls buyer, seller, referral and royalty addresses, the only real cost is
transaction fees; the cycle is repeatable until supply targets are met.

---

## Evidence

### Regression test (local, verbatim)
```
=== RUN   TestMarketKApp_ExecuteBuyMarket_RoyaltyReferralInflation
=== RUN   TestMarketKApp_ExecuteBuyMarket_RoyaltyReferralInflation/FixDisabled_MintsKLVFromThinAir
=== RUN   TestMarketKApp_ExecuteBuyMarket_RoyaltyReferralInflation/FixEnabled_RejectsInflation
--- PASS: TestMarketKApp_ExecuteBuyMarket_RoyaltyReferralInflation (0.00s)
    --- PASS: TestMarketKApp_ExecuteBuyMarket_RoyaltyReferralInflation/FixDisabled_MintsKLVFromThinAir (0.00s)
    --- PASS: TestMarketKApp_ExecuteBuyMarket_RoyaltyReferralInflation/FixEnabled_RejectsInflation (0.00s)
PASS
ok  	github.com/klever-io/klever-go/core/kapp/market	0.279s
```
`FixDisabled` asserts the attacker balance equals `2·bid = 51,200,000 KLV` for a single settlement
(`bid = 25,600,000 KLV`), with `bid` of that minted. `FixEnabled` asserts rejection and a `0`
balance.

### Mainnet exploitation (observed)
The bug was exploited in production, and was **detected and characterised externally** by the
community monitoring project **[KleverPuls / kpulse.tech](https://kpulse.tech)** before the root
cause was known internally. Over a ~24h window kpulse isolated a single wallet (opened
**2026-06-04**, ~**204 transactions** in ~24h, funded only by a ~**242K KLV KuCoin withdrawal**, no
treasury/foundation funding) that:

- **self-issued 3 NFT collections named "InflationPOC"** and **wash-traded one (`NFLATION-ESGO/1`)
  29 times** through self-created marketplaces — ~**$450K of artificial, economically empty NFT
  volume**;
- **swapped the proceeds KLV → USDC / USDT / WBTC / WETH on KleverSwap** and **bridged ~$72K of value
  to Ethereum** via wrapped-asset burns over 24h (USDC −12,487 ≈ $12.5K; USDT −26,362 ≈ $26.4K; WBTC
  −0.31 ≈ $19.6K; WETH −7.55 ≈ $14K);
- surfaced a spurious **"1.86B KLV outflow"** headline that kpulse correctly identified as a
  wash-trade **receipt-doubling** artifact with small real net KLV flow.

That "doubling of marketplace receipts" is **precisely the on-chain signature of this bug**: each
abusive settlement pays out a referral cut (`bid`) **plus** a royalty cut (`bid`) while the buyer paid
only `bid` once — the market contract emits ~2× the value it took in, which *is* the mint. The
attacker's self-issued collection and self-created marketplaces are exactly the self-dealing setup the
regression test reproduces (the test reuses the real on-chain identifiers: `collectionID =
"NFLATION-ESGO"`, asset `1`, market name "Inflation Market").

kpulse could not determine the cause from on-chain data alone and flagged the activity for
confirmation; the Klever core team then traced it to the referral+royalty settlement defect described
above and shipped the emergency guard + protocol fix.

Each abusive settlement minted one `bid` of KLV; the observed `bid` was `25,600,000 KLV`, repeated and
funnelled through a short hop chain before being swapped and bridged. The emergency guard
(`common/emergencyGuard.go`) blocks the following observed sender public keys (hex):

| Public key (hex) | Address | Role (observed) |
|---|---|---|
| `54ea28e527d4136508be955374afa54a8c25c19a48c674f412f7ce02db0f4e1b` | `klv12n4z3ef86sfk2z97j4fhfta9f2xztsv6frr8faqj7l8q9kc0fcdsfjfqez` | root / minter |
| `bb687dbba23e1844fec674a32cb8809f0d3207506c53fc3d637e40dc56708d63` | `klv1hd58mwaz8cvyflkxwj3jewyqnuxnyp6sd3flc0tr0eqdc4ns343skngdjq` | collector hop (~125M KLV) |
| `77388d3dfe6cd88e8da723254c11abf3d9cccb6fb77b000e5038fc3ff92b964d` | `klv1wuug6007dnvgard8yvj5cydt70vuejm0kaasqrjs8r7rl7ftjexsglalf6` | direct recipient (25.6M, idle) |
| `a196789b026f996867f08317cc6c5a4eb9ad3a59b1be3716420bc8692d4c3048` | `klv15xt83xczd7vkselssvtucmz6f6u66wjekxlrw9jzp0yxjt2vxpyq2nawrw` | hop-2 recipient (25M) |

The single-`bid` per-settlement size (25.6M KLV) matches the "direct recipient, 25.6M" entry, and the
~125M at the collector hop is consistent with roughly five abusive settlements.

---

## Impact

- **Unbounded inflation of KLV** (and of any sale currency used for the listing), repeatable for only
  transaction fees, by any account that creates its own collection + marketplace.
- The minted KLV is created by direct `AddToBalance` to attacker addresses (no tracked `Mint`), so
  the asset's booked supply does not change — the inflation is **off the books** and only detectable
  by summing balances / auditing receipts (it surfaces on-chain as *doubled* marketplace receipts).
- **Realized impact (observed):** the attacker minted KLV via ~29 self-dealt settlements, swapped to
  stable/wrapped assets on KleverSwap, and **off-ramped ~$72K to Ethereum via the bridge** (USDC,
  USDT, WBTC, WETH) before the emergency guard halted the activity, alongside ~$450K of artificial
  NFT wash-trade volume.
- Total loss of economic integrity for all KLV / token holders.

## Who can exploit it / prerequisites

- **Any account** that can pay the one-time collection-create + marketplace-create fees and tx
  fees. No roles, admin, or allowlist.
- **Any client.** The settlement is triggered by standard `MarketBuy` / `Claim` contracts POSTed to
  the public, unauthenticated `/transaction/send` RPC (`network/api/transaction/routes.go`,
  `SendTX` / `BroadcastTX`). The `operator` CLI, the SDKs, or a hand-signed `curl` all work.
- Deterministic; the abusive state is reached with one extra `UpdateRoyalties` after a normal listing.

---

## Remediation

Shipped as a layered response (embargoed):

### Layer 0 — emergency guard (deployed first, fork-proof) — `GHSA-p7gw` rc1
`common/emergencyGuard.go` + `data/transaction/emergencyGuard.go`: matching transactions are kept
out of blocks this node proposes (`core/process/block/preprocess/transactions.go`) and refused at
the node API (`node.go` `SendTransaction` / `SendBulkTransactions`). It **never changes block
validity**, so a partial-fleet rollout cannot fork the chain. It blocks the known attacker senders
(all contract types) plus all `MarketBuy`, `Sell`, and `CreateMarketplace` / `ConfigMarketplace`
operations while the protocol fix rolls out. Enforcement is by proposer cooperation, not protocol —
coverage equals the share of block producers running the guard.

### Layer 1 — protocol fix (consensus, epoch-gated) — `GHSA-p7gw` rc2
`core/kapp/market/market.go:593` rejects the settlement when `marketOwnerAmount < 0`, **before any
payout runs**, returning `Transaction_AmountInvalid`. Gated behind the new `FixMarketBuyOverflow`
activation-epoch flag (`config/enableEpochs.*`, `core/fork/forks.go`, `core/interface.go`) so
historical blocks reprocess identically. Covered by
`TestMarketKApp_ExecuteBuyMarket_RoyaltyReferralInflation`.

### Recommended hardening (defense in depth)
1. **Snapshot the royalty %** into `MarketOrderData` at `Sell` (as referral already is) and pay from
   the snapshot, eliminating the TOCTOU entirely; or re-evaluate the combined
   `referral% + royalty% <= 100%` invariant at settlement.
2. Treat a **negative** seller remainder as a hard error everywhere, and only treat exactly `0` as a
   no-op skip (`computeMarketOwnerAmount`), so a future regression aborts the tx instead of minting.
3. After splitting a payment pool, **assert conservation** (`referral + royalties + ownerShare == bid`)
   so any drift aborts the transaction.

---

## Notes

- Triggered by both BuyItNow (`Buy`) and auction settlement (`Claim`).
- The same family of "pay full cut, silently drop the negative remainder" minting also exists in the
  royalty-split paths and is tracked separately under **GHSA-cgc5-v3f2-8m2v** (split-royalty `uint32`
  overflow). This advisory covers the top-level referral+royalty > bid case; the
  `FixMarketBuyOverflow` guard here only checks `marketOwnerAmount`, not intra-split over-payments.

## Acknowledgments

- **[KleverPuls / kpulse.tech](https://kpulse.tech)** — community monitoring project that **first
  detected and characterised the exploitation in the wild**. kpulse isolated the attacker wallet and
  its "InflationPOC" collections, identified the marketplace wash-trading of `NFLATION-ESGO/1` and the
  KleverSwap → bridge off-ramp (~$72K to Ethereum), and flagged the anomalous *doubling* of
  marketplace receipts — the exact on-chain signature of this bug — prompting the incident response
  that led to this fix. The root cause was then identified and remediated by the Klever core team.

## Source

- Vulnerable / fixed code: `core/kapp/market/market.go:540-545,575-596,908,997-998`,
  `core/kapp/kda/trigger.go:613-676`, `core/process/kda/assetHelper.go:101`,
  `tools/converters.go:102`, `core/constants.go:18`.
- Emergency guard: `common/emergencyGuard.go`, `data/transaction/emergencyGuard.go`,
  `core/process/block/preprocess/transactions.go`, `node/node.go`.
- Fork flag: `config/enableEpochs.go`, `config/node/enableEpochs.yaml`, `core/fork/forks.go`,
  `core/interface.go`.
- Regression test: `core/kapp/market/market_test.go`
  (`TestMarketKApp_ExecuteBuyMarket_RoyaltyReferralInflation`).

## References
- https://github.com/klever-io/klever-go/security/advisories/GHSA-p7gw-2pcp-5pf8
- https://github.com/klever-io/klever-go/commit/8bcc600b0ac88070740c63c7ce1c8a968dd85251
- https://github.com/klever-io/klever-go
- https://github.com/klever-io/klever-go/releases/tag/v1.7.19
