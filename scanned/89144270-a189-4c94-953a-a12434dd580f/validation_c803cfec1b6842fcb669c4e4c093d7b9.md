### Title
Hardcoded 1:1 stablecoin conversion in `pallet-psm` allows reserve-draining arbitrage on external stablecoin de-peg - (File: `substrate/frame/psm/src/lib.rs`)

### Summary
`pallet-psm` implements a Peg Stability Module that swaps an internal stablecoin for approved external stablecoins (e.g. USDC, USDT) at a hardcoded 1:1 rate (adjusted only for decimals), with no price oracle input. This is the same pattern flagged in the external report: any de-peg of an approved external asset can be exploited by an unprivileged user before governance reacts.

### Finding Description
The pallet's own documentation states the swap is 1:1 by design: "Instantiable Peg Stability Modules (PSMs). Each PSM enables 1:1 swaps between an internal stablecoin and one or more approved external stablecoins" [1](#0-0) , and "PSM Debt: Total internal asset minted through a PSM, backed 1:1 by external assets in that PSM's reserve" [2](#0-1) .

Conversion between internal and external units is a pure decimal-scaling operation, with no market-price component: [3](#0-2) 

The only "peg defense" mechanisms are fee spreads, per-asset debt ceilings/weights, and circuit breakers that must be manually triggered by an admin origin (`Full` or `Emergency`) — none are price/oracle driven: [4](#0-3) [5](#0-4) 

This mirrors exactly the pattern in the external report: a lending/stability protocol treats a "stablecoin" as always worth $1 with no oracle check, so if the external asset (e.g. USDC/USDT) de-pegs downward, arbitrageurs can mint the internal asset 1:1 with the depreciated external asset and immediately redeem/sell the internal asset for full value elsewhere, or redeem other, still-solvent external assets from the shared reserve at par — draining the PSM's reserve of the healthy asset while leaving it holding the devalued one.

### Impact Explanation
If a governance-approved external asset (USDC/USDT-equivalent) de-pegs even briefly (as the report cites historically, USDT dropping to $0.95), any unprivileged, signed account can call `mint` to convert cheap external tokens into internal tokens at par, then `redeem` those internal tokens for a different, still fully-pegged external asset in the same PSM instance (when multiple externals are approved on one instance) — directly draining protocol reserves and socializing losses onto the PSM's internal-asset holders. Because circuit breakers require an admin (`Full`/`Emergency` origin) to react (`set_asset_status`), there is a window during which any user can exploit the stale peg. The severity depends on external asset liquidity/weight in the PSM and how quickly governance intervenes, but the loss is directly quantifiable as the amount of debt minted against the depegged asset before the circuit breaker or debt ceiling halts it, which the PR history itself acknowledges: "the internal stablecoin can depeg to the upside... Arbitrageurs can no longer deposit external stablecoins to mint and sell internal above peg" [6](#0-5)  — confirming the team's own mental model treats these hardcoded 1:1 swaps as the mechanism that both stabilizes and, in a de-peg scenario, threatens the peg/reserve.

### Likelihood Explanation
This is reachable by any unprivileged signed account calling the public `mint`/`redeem` extrinsics; no privileged role is required to trigger the exploit itself (only the reactive mitigation depends on a privileged admin). Likelihood is tied to real-world external stablecoin de-peg events, which have historical precedent (USDT 2022, as cited in the report) — this is a known, recurring risk category for any 1:1-peg mechanism holding third-party stablecoins as collateral.

### Recommendation
This is however a deliberate, documented design choice of a "Peg Stability Module" pattern, analogous to MakerDAO's PSM, which is intentionally oracle-free and instead relies on debt ceilings, per-asset ceiling weights, and circuit breakers as its risk controls. I was not able to fully verify within this pass whether additional automated (non-governance-triggered) safety mechanisms exist elsewhere in the runtime configuration (e.g., a `pallet-asset-rate`-style external price feed gating PSM operations, or an automatic pausing mechanism tied to on-chain price data) that would reduce the reaction-time gap; this would need to be confirmed by reading the concrete runtime integration (`asset-hub-westend-runtime`) and any monitoring/automation around it. If no such automated safeguard exists, recommend either: (1) integrating a price-deviation check (e.g., via an oracle or AMM-derived reference price) that pauses minting automatically once an external asset trades outside a configurable band, rather than relying solely on manual `Emergency`/`Full` origin intervention, or (2) tightening per-asset debt ceilings/weights and adding automatic, permissionless "circuit breaker" triggers based on measurable off-chain price feeds to reduce the reaction window.

### Proof of Concept
Conceptual (not from a live PoC, since this requires simulating a real external-asset de-peg):
1. PSM instance `I` has two approved externals, `USDC` and `USDT`, both healthy at par, each with non-zero `AssetCeilingWeight` and combined reserve backing `PsmDebt`.
2. `USDT` de-pegs to $0.95 on secondary markets while still tracked at 1:1 by `pallet-psm`.
3. Attacker acquires discounted `USDT` off-chain, calls `Psm::mint(origin, internal_asset=I, asset_id=USDT, external_amount, ...)` to receive internal asset at full par value, per the 1:1 conversion in `external_to_internal` [7](#0-6) .
4. Attacker calls `Psm::redeem(origin, internal_asset=I, asset_id=USDC, amount, ...)` to withdraw healthy `USDC` from the shared reserve at par, realizing an arbitrage profit equal to the de-peg discount, minus the ~0.5%/0.5% mint/redeem fees [8](#0-7) .
5. Repeat until `PsmDebt`/ceiling weight for `USDT` is exhausted or an admin manually disables the asset via `set_asset_status`, by which point the reserve's healthy `USDC` balance has been partially drained in exchange for the devalued `USDT`.

### Citations

**File:** substrate/frame/psm/src/lib.rs (L18-21)
```rust
//! # Peg Stability Module (PSM) Pallet
//!
//! Instantiable Peg Stability Modules (PSMs). Each PSM enables 1:1 swaps between an internal
//! stablecoin and one or more approved external stablecoins, typically to maintain a peg.
```

**File:** substrate/frame/psm/src/lib.rs (L59-61)
```rust
//! * **Reserve**: External asset balance held by a PSM's reserve account (derived, not stored).
//! * **PSM Debt**: Total internal asset minted through a PSM, backed 1:1 by external assets in that
//!   PSM's reserve.
```

**File:** substrate/frame/psm/src/lib.rs (L1575-1598)
```rust
		/// Convert an amount denominated in external-asset units into internal units.
		///
		/// Scales by `10^(ext_decimals - internal_decimals)` — multiplies up when internal has more
		/// decimals, floor-divides when it has fewer. Returns [`Error::ConversionOverflow`] if
		/// the scaling factor or the product does not fit in the balance type.
		pub(crate) fn external_to_internal(
			amount: BalanceOf<T>,
			ext_decimals: u8,
			internal_decimals: u8,
		) -> Result<BalanceOf<T>, Error<T>> {
			use core::cmp::Ordering::*;
			match ext_decimals.cmp(&internal_decimals) {
				Equal => Ok(amount),
				Less => {
					let diff = (internal_decimals - ext_decimals) as u32;
					let factor = Self::pow10(diff)?;
					amount.checked_mul(&factor).ok_or(Error::<T>::ConversionOverflow)
				},
				Greater => {
					let diff = (ext_decimals - internal_decimals) as u32;
					let factor = Self::pow10(diff)?;
					Ok(amount.checked_div(&factor).unwrap_or_else(BalanceOf::<T>::zero))
				},
			}
```

**File:** substrate/frame/psm/README.md (L80-91)
```markdown
## Fee Structure

Fees are stored per `(internal_asset, external_asset)` pair, calculated using
`Permill::mul_ceil` (rounds up), and routed to the instance's `fee_destination`:

- **Minting Fee**: `fee = MintingFee[internal, external].mul_ceil(internal_equivalent)`
  -- deducted from internal-asset output, minted to `fee_destination`
- **Redemption Fee**: `fee = RedemptionFee[internal, external].mul_ceil(amount)`
  -- transferred from the user to `fee_destination`

With 0.5% fees on both sides, arbitrage opportunities exist when the internal
asset trades outside $0.995-$1.005.
```

**File:** substrate/frame/psm/README.md (L93-105)
```markdown
## Circuit Breaker

Each approved external on each instance has an independent circuit breaker
with three levels:

| Level             | Minting | Redemption | Use Case                          |
| ----------------- | ------- | ---------- | --------------------------------- |
| `AllEnabled`      | Allowed | Allowed    | Normal operation                  |
| `MintingDisabled` | Blocked | Allowed    | Drain debt from a problematic external |
| `AllDisabled`     | Blocked | Blocked    | Full emergency halt of an external |

`set_asset_status` is callable at both the `Full` (`full_admin`) and
`Emergency` (`emergency_admin`) levels.
```

**File:** substrate/frame/psm/README.md (L112-121)
```markdown
| Extrinsic | Required Level | Description |
| --- | --- | --- |
| `set_minting_fee(internal_asset, asset_id, fee)` | Full | Update minting fee for the pair |
| `set_redemption_fee(internal_asset, asset_id, fee)` | Full | Update redemption fee for the pair |
| `set_max_debt(internal_asset, value)` | Full or Emergency | Update absolute debt ceiling for the PSM |
| `set_asset_ceiling_weight(internal_asset, asset_id, weight)` | Full or Emergency | Update external ceiling weight |
| `set_asset_status(internal_asset, asset_id, status)` | Full or Emergency | Set per-external circuit breaker level |
| `add_external_asset(internal_asset, asset_id)` | Full | Approve external on a PSM |
| `remove_external_asset(internal_asset, asset_id)` | Full | Remove external from a PSM (zero debt) |

```

**File:** prdoc/stable2606/pr_12012.prdoc (L10-16)
```text
      `emergency_origin_can_set_max_psm_debt`.

    When the max PSM debt is reached, minting is blocked and the internal stablecoin
    can depeg to the upside. Arbitrageurs can no longer deposit external stablecoins
    to mint and sell internal above peg, so demand pressure has nowhere to relieve.

    Allowing the Emergency origin to raise the ratio restores the arbitrage path.
```
