### Title
Router-level liquidity provision in the `swap` example package mints LP tokens with no minimum-liquidity slippage check, enabling sandwich attacks that steal LP value - ([File: aptos-move/move-examples/swap/sources/router.move])

### Summary
The Sherlock report's custody invariant is: *"a depositor's minted share of a pooled asset must be protected against price manipulation immediately preceding their deposit; per-token minimum-amount checks are not sufficient to protect the actual share/LP-token output."* The Aptos-native analog is Move-example `swap` package's `router::add_liquidity_entry` / `router::optimal_liquidity_amounts` and `liquidity_pool::mint`, which hold and account for FungibleAsset reserves in an Aptos object-based pool (`LiquidityPool`, `FungibleStore`s, LP `Metadata`/`MintRef`). Exactly like the Multipool bug, these functions validate only per-token minimum amounts (`amount_1_min`, `amount_2_min`), never the resulting LP token quantity, so an attacker can sandwich a legitimate deposit by swapping in the same pool immediately before it, causing the depositor's minted LP share to be diluted relative to fair value while all on-chain slippage checks still pass.

### Finding Description
`router::optimal_liquidity_amounts` (aptos-move/move-examples/swap/sources/router.move:172-214) computes the optimal deposit amounts from the pool's *current* reserves and returns `(amount_1, amount_2, liquidity)`, but the third value (the actual LP token amount to be minted) is silently discarded by the caller:

```
public entry fun add_liquidity_entry(
    lp: &signer,
    token_1: Object<Metadata>,
    token_2: Object<Metadata>,
    is_stable: bool,
    amount_1_desired: u64,
    amount_2_desired: u64,
    amount_1_min: u64,
    amount_2_min: u64,
) {
    let (optimal_amount_1, optimal_amount_2, _) = optimal_liquidity_amounts(...);
    let optimal_1 = primary_fungible_store::withdraw(lp, token_1, optimal_amount_1);
    let optimal_2 = primary_fungible_store::withdraw(lp, token_2, optimal_amount_2);
    add_liquidity(lp, optimal_1, optimal_2, is_stable);
}
```
(router.move:218-240)

`liquidity_pool::mint` (liquidity_pool.move:387-439) computes the minted LP amount from the reserves at execution time:
```
let token_1_liquidity = math64::mul_div(amount_1, (lp_token_supply as u64), reserve_1);
let token_2_liquidity = math64::mul_div(amount_2, (lp_token_supply as u64), reserve_2);
math64::min(token_1_liquidity, token_2_liquidity)
```
with only `assert!(liquidity_token_amount > 0, EINSUFFICIENT_LIQUIDITY_MINTED)` as protection — no user-specified floor.

The custody invariant broken: `amount_1_min`/`amount_2_min` in `optimal_liquidity_amounts` only bound the *token amounts* deposited relative to the desired amounts and current (possibly manipulated) reserves — they do not bound the *LP token amount* actually minted to the depositor. An attacker can:
1. Front-run the victim's `add_liquidity_entry` transaction with a `swap` in the same pool (`token_1`/`token_2`, same `is_stable` flag), shifting `reserve_1`/`reserve_2` away from the price the victim expected.
2. The victim's `optimal_liquidity_amounts` recomputes `amount_2_optimal` from the new (skewed) reserves; because the ratio check (`amount_2_optimal >= amount_2_min`) is evaluated against the *already-skewed* ratio, it still passes even though the fair value of the LP tokens the victim will receive for their capital is now lower.
3. `liquidity_pool::mint` computes `liquidity_token_amount` from these skewed reserves and mints proportionally fewer LP tokens to the victim.
4. The attacker back-runs with an opposite swap to restore the price, realizing a profit extracted from the victim's deposit (classic ERC4626/Uniswap-add-liquidity sandwich), analogous to the "multiple fee tiers" mechanic in the Multipool bug where price manipulation across pools distorted the reserve ratio right before deposit.

This differs from the swap function itself, which correctly enforces `amount_out_min` against the actual output (`swap`, router.move:81-92) — the flaw is isolated to the liquidity-provision path, which has no equivalent floor on the LP output.

### Impact Explanation
This breaks the custody invariant that a liquidity provider's minted share must correspond to fair value contributed. The corrupted value is the `liquidity_token_amount` field computed inside `liquidity_pool::mint` (an object-held fungible-asset-standard LP token whose `MintRef`/`FungibleStore` custody the depositor's proportional claim on the pool's `FungibleStore`-held reserves). Funds lost are unbounded relative to the size of the deposit and the attacker's capital to skew reserves, and the loss is realized immediately and irreversibly upon deposit (no recovery path), matching the "unbounded funds at loss" reasoning that caused Sherlock to accept H-4 as a valid High.

### Likelihood Explanation
This is a `move-examples` reference package, not deployed core framework code, which lowers real-world likelihood versus a mainnet Move framework module — this is the main uncertainty affecting the finding's applicability, since the custody-impact gate targets mainnet-relevant impacts. However, if this router/liquidity_pool package (or any fork of it) is deployed as-is, the attack is a standard, cheap, deterministic MEV sandwich requiring only a swap transaction ordered immediately before and after the victim's `add_liquidity_entry` call — well within normal validator/searcher capabilities, with no privileged access required.

### Recommendation
Add a `min_liquidity` (or equivalent minimum-LP-token-out) parameter to `router::add_liquidity_entry` (and the coin variants) and to `liquidity_pool::mint`, and assert the actually-computed `liquidity_token_amount` (currently discarded via `_` in `optimal_liquidity_amounts`'s caller) is `>= min_liquidity`, mirroring the fix applied to the referenced Multipool contract (adding a minimum acceptable LP-mint check) and the pattern already used correctly in `router::swap` (`amount_out_min`).

### Proof of Concept
1. Pool `P` for `(token_1, token_2, is_stable=false)` has reserves `R1, R2` with `lp_token_supply = S`.
2. Victim submits `add_liquidity_entry(lp, token_1, token_2, false, amount_1_desired, amount_2_desired, amount_1_min, amount_2_min)` expecting LP tokens ≈ `f(amount_1_desired, amount_2_desired, R1, R2, S)`.
3. Attacker front-runs with `swap_entry` (or direct `swap`) on pool `P`, moving reserves to `R1', R2'` such that `amount_2_optimal' = mul_div(amount_1_desired, R2', R1')` still satisfies `amount_2_optimal' >= amount_2_min` (attacker tunes swap size to stay within victim's slippage tolerance).
4. Victim's transaction executes: `optimal_liquidity_amounts` returns `(amount_1, amount_2, liquidity')` computed from `R1', R2'`; the third value is discarded by `add_liquidity_entry`, so no check occurs; `liquidity_pool::mint` mints `liquidity' < liquidity` (the amount the victim would have received without manipulation) because `liquidity' = min(amount_1*S/R1', amount_2*S/R2')` is depressed by the manipulated reserves.
5. Attacker back-runs with the opposite `swap` to restore `R1, R2`, extracting the value difference (net of swap fees) from the victim's now-under-minted LP position.
6. No assertion anywhere in `router.move` or `liquidity_pool.move` compares the minted `liquidity_token_amount` to a caller-supplied floor, confirming the missing custody check.